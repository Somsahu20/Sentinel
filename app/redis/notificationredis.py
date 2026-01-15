import redis as rd
from ..db.notifications import NotificationResponse
from ..db.sessions import (
    SyncSessionLocal
)
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
import logging #! to log info to docker 
from fastapi import HTTPException
from sqlalchemy import select
from ..models.notifications import Notification, Status, Channel
from starlette.status import HTTP_404_NOT_FOUND
from twilio.rest import Client

acccount_sid = os.getenv("SID")
auth_token = os.getenv("AUTHTOKEN")
phone_num = os.getenv("PHONE")
client = Client(acccount_sid, auth_token)
email_api = os.getenv("SEND_GRID_API")
email = os.getenv("EMAIL") 



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SentinelRedis")

host = os.getenv("REDIS_HOST", "redis-db")
r = rd.Redis(host=host, port=6379, decode_responses=True)
QUEUE = "sentinel:notifications"
GROUP = "manager"

TESTGRP = "Alice"



def setup_redis():

    try:
        r.xgroup_create(QUEUE, GROUP, id="$", mkstream=True)
        logger.info("Group created")
    except Exception as err:

        if 'BUSYGROUP' in str(err):
            logger.info(f"{GROUP} already created")
        else:
            logger.error("There is an error in setting up the group")
            raise err


def push_to_queue(n: NotificationResponse):

    try:
        n_dict = n.model_dump(mode='json', exclude={"created_at", "updated_at"})

        r.xadd(QUEUE, fields=n_dict) # type: ignore 
        return 1 #! Indicates successful in execution

    except Exception as err:
        print("There is an error in push to queue", err)
        return -1 #! Indicated failure in execution
    
def read_tasks(worker):

    try:
        res2 = r.xreadgroup(GROUP, worker, streams={QUEUE: ">"}, count=2, block=5000)
        if res2:
            stream, li = res2[0] #type: ignore 
            return li
        else:
            return []

    except Exception as err:
        logger.error(f"This is the error {err}")
        return []




def send_sms(body, recipient) -> bool:
    try:
        if not client:
            logger.warning("Twilio Client not initialized")
            return False
            
        client.messages.create(
            body=body,
            from_=phone_num,
            to=recipient
        )
        logger.info(f"SMS sent to {recipient}")
        return True
    except Exception as e:
        logger.error(f"Twilio Error: {e}")
        return False

def send_email(body, recipient) -> bool:
    try:
        if not email_api:
            logger.warning("SendGrid API Key missing")
            return False

        message = Mail(
            from_email=email,
            to_emails=recipient,
            subject="Message from Sentinel",
            plain_text_content=body
        )
        sg = SendGridAPIClient(email_api)
        response = sg.send(message)
        
        if 200 <= response.status_code < 300:
            logger.info(f"Email sent to {recipient}")
            return True
        else:
            logger.error(f"SendGrid failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"SendGrid Error: {e}")
        return False

def process_each_task(task) -> bool:
    try:
        id, task_dict = task
        
        body = task_dict.get("body")
        recipient = task_dict.get("recipient")
        channel_str = task_dict.get("channel") 
        
        if not body or not recipient or not channel_str:
            logger.error(f"Invalid Payload: Missing body, recipient, or channel. Data: {task_dict}")
            return False

        if channel_str == Channel.SMS.value:
            return send_sms(body, recipient)
            
        elif channel_str == Channel.EMAIL.value:
            return send_email(body, recipient)
            
        else:
            logger.error(f"Unknown Channel: {channel_str}")
            return False

    except Exception as err:
        logger.error(f"Critical Worker Error: {err}")
        return False

def ack_del(task) -> bool:

    sync_db = SyncSessionLocal() #! ALways close when you get connection of db like this

    try:
        id, task_dict = task

        db_id = task_dict.get("id")
        stmt = select(Notification).where(Notification.id == db_id)
        res = sync_db.execute(stmt).scalar_one_or_none()

        if not res:
            logger.error("No such task with this id")
            return False

    

        if process_each_task(task):
    
            r.xack(QUEUE, GROUP, id)
            r.xdel(QUEUE, id)
            if res.status == Status.FAILED:
                res.retry_cnt += 1
            res.status = Status.SENT #todo change it to enum type sent    
            sync_db.commit()
            sync_db.refresh(res)
                
            return True
        else:
            res.status = Status.FAILED #todo change it to enum type failed
            sync_db.commit()
            sync_db.refresh(res)

            return False

    except Exception as err:
        logger.info(f"Error in acknowledging and deleting the task\n", err)
        sync_db.rollback()
        sync_db.close()
        return False
    finally:
        sync_db.close()
    

def assign_pending_task(worker, start):

    try:
        res = r.xpending(QUEUE, GROUP)
        if res['pending'] > 0: #type:ignore
            claim = r.xautoclaim(QUEUE, GROUP, worker, 60000, start_id=start, count=3)

            new_start = claim[0] #type: ignore
            rem_task = claim[1] #type: ignore

            if rem_task:
                for task in rem_task:
                    ack_del(task=task)

            return new_start
        else: #! it means no pending lists so return "0-0"
            return "0-0"

    except Exception as err:
        logger.info(f"Error in functiom assign pending tasks\n {err}")
        return "0-0"

    
