import os
import time

from celery import Celery
from configs.env import *

celery = Celery(__name__)
celery.conf.broker_url = os.getenv("CELERY_BROKER_URL")
celery.conf.result_backend = os.getenv("CELERY_RESULT_BACKEND")


# @celery.task(name="create_task")
# def create_task(a, b, c):
#     time.sleep(a)
#     return b + c