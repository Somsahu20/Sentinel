import redis as rd
from ..db.notifications import NotificationResponse
import os
import logging #! to log info to docker 
import time

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


def process_each__task(task) -> bool:
    try:
        id, task_dict = task
        #? Mimicking the api call for twilio to send SMS or use API to send mails
        time.sleep(3)
    

        #todo here after all logic is written, we'll apply twilio logic here to send sms and check for phone number or passsword
            
        return True

    except Exception as err:
        logger.error(f"This is the error in process task:\n {err}")
        return False

def ack_del(task) -> bool:

    try:
        id, task_dict = task
        if process_each__task(task):
            r.xack(QUEUE, GROUP, id)
            r.xdel(QUEUE, id)
            if "status" in task_dict:
                task_dict["status"] = "sent" #todo change it to enum type sent
            return True
        else:
            if "status" in task_dict:
                task_dict["status"] = "failed" #todo change it to enum type failed
            return False

    except Exception as err:
        logger.info(f"Error in acknowledging and deleting the task")
        return False
    
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

    
    
    
