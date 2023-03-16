import os
import time
from celery import Celery
from configs.env import *
from rails_client import client
from services.fcl_freight_rate.interaction.create_fcl_freight_rate import create_fcl_freight_rate

CELERY_CONFIG = {
    "enable_utc": True,
    "task_serializer": "pickle",
    "event_serializer": "pickle",
    "result_serializer": "json",
    "accept_content": ['application/json', 'application/x-python-serialize']
}
celery = Celery(__name__)
celery.conf.broker_url = os.getenv("CELERY_BROKER_URL")
celery.conf.result_backend = os.getenv("CELERY_RESULT_BACKEND")
celery.conf.update(**CELERY_CONFIG)

@celery.task()
def create_fcl_freight_rate_delay(request):
    return create_fcl_freight_rate(request)


