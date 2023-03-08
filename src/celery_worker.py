import os
import time
from services.fcl_freight_rate.interaction.create_fcl_freight_rate import create_fcl_freight_rate_data
from services.freight_trend.interactions.create_freight_trend_port_pair import create_freight_trend_port_pair
from celery import Celery
from configs.env import *
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

@celery.task(name="create_task")
def create_task(param):
    from rails_client.client import initialize_client
    initialize_client()
    rate = create_fcl_freight_rate_data(param)


@celery.task()
def create_freight_trend_port_pair_celery(origin_port_id,destination_port_id):
    create_freight_trend_port_pair(origin_port_id,destination_port_id)

