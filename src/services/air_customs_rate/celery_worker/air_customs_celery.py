from celery import Celery
from services.air_customs_rate.helpers import update_organization_air_customs
from services.air_customs_rate.interaction.create_air_customs_rate import create_air_customs_rate
from services.fcl_freight_rate.helpers.get_multiple_service_objects import get_multiple_service_objects
from kombu.serialization import registry
from configs.env import *
from kombu import Exchange, Queue

CELERY_CONFIG = {
    "enable_utc": True,
    "task_serializer": "pickle",
    "event_serializer": "pickle",
    "result_serializer": "pickle",
    "accept_content": ['application/json', 'application/x-python-serialize'],
    "task_acks_late": True,
    "result_expires": 60*30,
    "celeryd_prefetch_multiplier": 1
}

if APP_ENV == 'development':
    CELERY_REDIS_URL = 'redis://@127.0.0.1:6379/0'

celery = Celery(__name__)
registry.enable("pickle")
celery.conf.broker_url = CELERY_REDIS_URL
celery.conf.result_backend = CELERY_REDIS_URL
celery.conf.broker_transport_options = {
    'queue_order_strategy': 'priority',
    'visibility_timeout': 14400
}

celery.conf.low_queues = [Queue('low', Exchange('low'), routing_key='low',
          queue_arguments={'x-max-priority': 6})]
celery.conf.update(**CELERY_CONFIG)

@celery.task(bind = True, retry_backoff=True, max_retries=5)
def air_customs_functions_delay(self,air_customs_object,request):
    try:
        update_organization_air_customs(request)
        get_multiple_service_objects(air_customs_object)

    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, max_retries=5, retry_backoff = True)
def bulk_operation_perform_action_functions_air_customs_delay(self, action_name, object):
    try:
        eval(f"object.perform_{action_name}_action()")
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, retry_backoff=True, max_retries=5)
def create_air_customs_rate_delay(self, request):
    try:
        return create_air_customs_rate(request)
    except Exception as e:
        if type(e).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= e)