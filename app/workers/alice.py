import redis as rd
import os
import logging #! to log info to docker 
from ..redis.notificationredis import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SentinelRedis")

host = os.getenv("REDIS_HOST", "redis-db")
r = rd.Redis(host=host, port=6379, decode_responses=True)

setup_redis()
start_time = "0-0"

workers = ["Alice", "Bob", "Catherine"]

while True:

    try:
        #todo Doing tasks
        for worker in workers:
            task_list = read_tasks(worker=worker)
            if task_list:
                for task in task_list:
                    ack_del(task=task)

            start_time = assign_pending_task(worker, start_time)

    except Exception as err:
        logger.error(f"The error is {err}")
    
