from celery import Celery
from kombu.serialization import registry
from configs.env import *
from micro_services.client import organization, common, spot_search
from libs.get_multiple_service_objects import get_multiple_service_objects
from services.rate_sheet.interactions.validate_and_process_rate_sheet_converted_file import validate_and_process_rate_sheet_converted_file
from services.ftl_freight_rate.scheduler.fuel_scheduler import fuel_scheduler
from services.haulage_freight_rate.schedulers.electricity_price_scheduler import electricity_price_scheduler
from kombu import Exchange, Queue
from celery.schedules import crontab
from services.chakravyuh.interaction.get_air_invoice_estimation_prediction import invoice_rates_updation
from database.rails_db import get_past_cost_booking_data
from services.extensions.interactions.create_freight_look_surcharge_rates import create_surcharge_rate_api
# Rate Producers

from services.chakravyuh.producer_vyuhs.fcl_freight import FclFreightVyuh as FclFreightVyuhProducer

# Dynamic Pricing

from services.chakravyuh.setters.fcl_freight import FclFreightVyuh as FclFreightVyuhSetter
from services.chakravyuh.setters.fcl_booking_invoice import FclBookingVyuh as FclBookingVyuhSetters
from playhouse.postgres_ext import ServerSide
from services.fcl_freight_rate.workers.fcl_freight_critical_port_pairs_scheduler import (
    fcl_freight_critical_port_pairs_scheduler,
)
from services.fcl_freight_rate.workers.fcl_freight_cancelled_shipments_scheduler import (
    fcl_freight_cancelled_shipments_scheduler,
)
from services.fcl_freight_rate.workers.fcl_freight_expiring_rates_scheduler import (
    fcl_freight_expiring_rates_scheduler,
)
from services.air_freight_rate.workers.air_freight_cancelled_shipments_scheduler import (
    air_freight_cancelled_shipments_scheduler,
)
from services.air_freight_rate.workers.air_freight_critical_port_pairs_scheduler import (
    air_freight_critical_port_pairs_scheduler,
)
from services.air_freight_rate.workers.air_freight_expiring_rates_scheduler import (
    air_freight_expiring_rates_scheduler,
)
from services.haulage_freight_rate.workers.haulage_freight_expiring_rates_scheduler import (
    haulage_freight_expiring_rates_scheduler,
)


CELERY_CONFIG = {
    "enable_utc": True,
    "task_serializer": "pickle",
    "event_serializer": "pickle",
    "result_serializer": "pickle",
    "accept_content": ['application/json', 'application/x-python-serialize'],
    "task_acks_late": True,
    "result_expires": 60*30,
    "celeryd_prefetch_multiplier": 2,
    "celery_queue_max_length": 1000
}

if APP_ENV == 'development':
    CELERY_REDIS_URL = 'redis://@127.0.0.1:6379/0'

celery = Celery(__name__)
registry.enable("pickle")
celery.conf.broker_url = CELERY_REDIS_URL
celery.conf.result_backend = CELERY_REDIS_URL
celery.conf.broker_transport_options = {
    'queue_order_strategy': 'priority',
    'visibility_timeout': 86400
}
celery.conf.critical_queues = [Queue('critical', Exchange('critical'), routing_key='critical',
          queue_arguments={'x-max-priority': 6})]
celery.conf.communication_queues = [Queue('communication', Exchange('communication'), routing_key='communication',
          queue_arguments={'x-max-priority': 6})]
celery.conf.bulk_operation_queues = [Queue('bulk_operations', Exchange('bulk_operations'), routing_key='bulk_operations',
          queue_arguments={'x-max-priority': 4})]
celery.conf.statistics_queues = [Queue('statistics', Exchange('statistics'), routing_key='statistics',
          queue_arguments={'x-max-priority':2})]
celery.conf.fcl_freight_rate_queues = [Queue('fcl_freight_rate', Exchange('fcl_freight_rate'), routing_key='fcl_freight_rate',
          queue_arguments={'x-max-priority': 2})]
celery.conf.low_queues = [Queue('low', Exchange('low'), routing_key='low',
          queue_arguments={'x-max-priority': 2})]

celery.conf.update(**CELERY_CONFIG)
celery.conf.beat_schedule = {
    'fcl_freigh_rates_to_cogo_assured': {
        'task': 'services.fcl_freight_rate.fcl_celery_worker.fcl_freight_rates_to_cogo_assured',
        'schedule': crontab(minute=0, hour='*/2'),
        'options': {'queue' : 'fcl_freight_rate'}
        },
    # 'update_cogo_assured_fcl_freight_rates': {
    #     'task': 'services.fcl_freight_rate.fcl_celery_worker.update_cogo_assured_fcl_freight_rates',
    #     'schedule': crontab(minute=30, hour=18),
    #     'options': { 'queue': 'fcl_freight_rate' }
    #     },
    'process_fuel_data_delays': {
        'task': 'celery_worker.process_fuel_data_delay',
        'schedule': crontab(minute=00,hour=21),
        'options': {'queue' : 'fcl_freight_rate'}
        },
    'process_electricity_data_delays': {
        'task': 'celery_worker.process_electricity_data_delays',
        'schedule': crontab(hour=4, minute=0, day_of_week='sat'),
        'options': {'queue' : 'fcl_freight_rate'}
    },
    # 'fcl_cost_booking_estimation':{
    #     'task': 'celery_worker.fcl_cost_booking_estimation',
    #     'schedule': crontab(minute=30,hour=18),
    #     'options': {'queue' : 'fcl_freight_rate'}
    # },
    'cluster_extension_by_latest_trends_worker':{
        'task': 'services.fcl_freight_rate.fcl_celery_worker.cluster_extension_by_latest_trends_worker',
        "schedule": crontab(hour=23, minute=00),
        'options': {'queue': 'fcl_freight_rate'}
    },
    'cache_data_worker':{
        'task': 'services.bramhastra.celery.cache_data_worker_in_delay',
        'schedule': crontab(hour=16, minute=00),
        'options': {'queue': 'low'}
    },
    'fcl_daily_attributer_updater':{
        'task': 'services.bramhastra.celery.fcl_daily_attributer_updater_in_delay',
        'schedule': crontab(hour = 22, minute = 00),
        'options': {'queue': 'statistics'}
    },
    "create_jobs_for_cancelled_shipments": {
        "task": "celery_worker.create_job_for_cancelled_shipments_delay",
        "schedule": crontab(hour=2, minute=30),
        "options": {"queue": "fcl_freight_rate"},
    },
    "create_jobs_for_expiring_rates": {
        "task": "celery_worker.create_job_for_expiring_rates_delay",
        "schedule": crontab(hour=00, minute=00),
        "options": {"queue": "fcl_freight_rate"},
    },
    "create_jobs_for_critical_port_pairs": {
        "task": "celery_worker.create_job_for_critical_port_pairs_delay",
        'schedule': crontab(hour=1, minute=00),
        "options": {"queue": "fcl_freight_rate"},
    },
    "update_fcl_freight_local_jobs_status_to_backlogs": {
        "task": "services.fcl_freight_rate.fcl_celery_worker.update_fcl_freight_rate_local_jobs_to_backlog_delay",
        "schedule": crontab(hour=22, minute=50),
        "options": {"queue": "fcl_freight_rate"}
    },
}


celery.autodiscover_tasks(['services.air_customs_rate.air_customs_celery_worker'], force=True)
celery.autodiscover_tasks(['services.haulage_freight_rate.haulage_celery_worker'], force=True)
celery.autodiscover_tasks(['services.ftl_freight_rate.ftl_celery_worker'], force=True)
celery.autodiscover_tasks(['services.bramhastra.celery'], force=True)
celery.autodiscover_tasks(['services.air_freight_rate.air_celery_worker'], force=True)
celery.autodiscover_tasks(['services.fcl_freight_rate.fcl_celery_worker'], force=True)
celery.autodiscover_tasks(['services.fcl_customs_rate.fcl_customs_celery_worker'], force=True)
celery.autodiscover_tasks(['services.ltl_freight_rate.ltl_celery_worker'], force=True)
celery.autodiscover_tasks(['services.lcl_freight_rate.lcl_celery_worker'], force=True)
celery.autodiscover_tasks(['services.lcl_customs_rate.lcl_customs_celery_worker'], force=True)
celery.autodiscover_tasks(['services.fcl_cfs_rate.fcl_cfs_celery_worker'], force=True)




@celery.task(bind = True, retry_backoff=True,max_retries=1)
def fcl_cost_booking_estimation(self):
    try:
        limit = 500
        offset = 0
        while True:
            cost_booking_data = get_past_cost_booking_data(limit, offset)
            offset += 500
            if not cost_booking_data:
                break

            for booking_data in cost_booking_data:
                setter = FclBookingVyuhSetters(booking_data)
                setter.set_dynamic_pricing()

    except Exception as exc:
        pass

@celery.task(bind = True, retry_backoff=True,max_retries=3)
def adjust_cost_booking_dynamic_pricing(self, new_rate,affected_transformation,new):
    try:
        fcl_freight_vyuh = FclBookingVyuhSetters(new_rate=new_rate)
        fcl_freight_vyuh.adjust_price_for_tranformation(affected_transformation=affected_transformation, new=new)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)


@celery.task(bind = True, max_retries=5, retry_backoff = True)
def update_multiple_service_objects(self, object):
    try:
        get_multiple_service_objects(object)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, max_retries=5, retry_backoff = True)
def send_closed_notifications_to_sales_agent_function(self, object):
    try:
        object.send_closed_notifications_to_sales_agent()
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, max_retries=5, retry_backoff = True)
def send_create_notifications_to_supply_agents_function(self, object):
    try:
        object.send_create_notifications_to_supply_agents()
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, max_retries=5, retry_backoff = True)
def set_relevant_supply_agents_function(self, object, request):
    try:
        object.set_relevant_supply_agents(request)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, max_retries=5, retry_backoff = True)
def send_notifications_to_supply_agents_local_request(self, object):
    try:
        object.send_notifications_to_supply_agents()
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, max_retries=5, retry_backoff = True)
def create_communication_background(self, data):
    try:
        common.create_communication(data)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, max_retries=5, retry_backoff = True)
def send_closed_notifications_to_sales_agent_local_request(self, object):
    try:
        object.send_closed_notifications_to_sales_agent()
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, max_retries=5, retry_backoff = True)
def send_closed_notifications_to_sales_agent_free_day_request(self, object):
    try:
        object.send_closed_notifications_to_sales_agent()
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, max_retries=5, retry_backoff = True)
def send_closed_notifications_to_sales_agent_feedback(self, object):
    try:
        object.send_closed_notifications_to_sales_agent()
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, max_retries=5, retry_backoff = True)
def send_closed_notifications_to_user_feedback(self, object):
    try:
        object.send_closed_notifications_to_user()
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, max_retries=5, retry_backoff = True)
def send_closed_notifications_to_user_request(self, object):
    try:
        object.send_closed_notifications_to_user()
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, max_retries=5, retry_backoff = True)
def bulk_operation_perform_action_functions(self, action_name,object,sourced_by_id,procured_by_id,cogo_entity_id):

    args = [f"sourced_by_id='{sourced_by_id}'", f"procured_by_id='{procured_by_id}'"] if sourced_by_id is not None and procured_by_id is not None else []
    if cogo_entity_id:
        args.append(f"cogo_entity_id='{cogo_entity_id}'")

    eval_string = f"object.perform_{action_name}_action({', '.join(args)})"
    
    try:
        eval(eval_string)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, max_retries=5, retry_backoff = True)
def air_freight_bulk_operation_delay(self, action_name,object,sourced_by_id,procured_by_id):
    try:
        eval(f"object.perform_{action_name}_action()")
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)


@celery.task(bind = True, max_retries=5, retry_backoff = True)
def update_freight_objects_for_commodity_surcharge(self, surcharge_object):
    try:
        surcharge_object.update_freight_objects()
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, retry_backoff=True,max_retries=5)
def validate_and_process_rate_sheet_converted_file_delay(self, request):
    try:
        return validate_and_process_rate_sheet_converted_file(request)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)


@celery.task(bind = True, retry_backoff=True,max_retries=5)
def update_contract_service_task_delay(self, object):
    try:
        common.update_contract_service_task(object)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, retry_backoff=True,max_retries=5)
def update_spot_negotiation_locals_rate_task_delay(self,object):
    try:
       common.update_spot_negotiation_locals_rate(object)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)


@celery.task(bind = True, retry_backoff=True,max_retries=3)
def extend_fcl_freight_rates(self, rate):
    try:
        fcl_freight_vyuh = FclFreightVyuhProducer(rate=rate)
        fcl_freight_vyuh.extend_rate()
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind=True, retry_backoff=True,max_retries=3)
def transform_dynamic_pricing(self, new_rate, current_validities, affected_transformation, new):
    try:
        fcl_freight_vyuh = FclFreightVyuhSetter(new_rate=new_rate, current_validities=current_validities)
        fcl_freight_vyuh.adjust_price_for_tranformation(affected_transformation=affected_transformation, new=new)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, retry_backoff=True,max_retries=3)
def adjust_fcl_freight_dynamic_pricing(self, new_rate, current_validities):
    try:
        fcl_freight_vyuh = FclFreightVyuhSetter(new_rate=new_rate, current_validities=current_validities)
        fcl_freight_vyuh.set_dynamic_pricing()
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)
    
@celery.task(bind = True, retry_backoff=True, max_retries=1)
def process_fuel_data_delay(self):
    try:
        fuel_scheduler()
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, retry_backoff=True, max_retries=1)
def process_electricity_data_delays(self):
    try:
        electricity_price_scheduler()
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)


@celery.task(bind = True, max_retries=5, retry_backoff = True)
def bulk_operation_perform_action_functions_fcl_customs_cfs_delay(self, action_name, object, sourced_by_id, procured_by_id):
    try:
        eval(f"object.perform_{action_name}_action(sourced_by_id='{sourced_by_id}',procured_by_id='{procured_by_id}')")
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, retry_backoff=True,max_retries=3)
def send_air_freight_rate_feedback_notification_in_delay(self,object,air_freight_rate,airports):
    try:
        object.send_notification_to_supply_agents(air_freight_rate,airports)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, retry_backoff=True,max_retries=3)
def process_freight_look_surcharge_rate_in_delay(self,rate, locations,commodity):
    try:
        create_surcharge_rate_api(rate, locations,commodity)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind=True, retry_backoff=True, max_retries=3)
def create_job_for_cancelled_shipments_delay(self):
    try:
        fcl_freight_cancelled_shipments_scheduler()
        air_freight_cancelled_shipments_scheduler()
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)


@celery.task(bind=True, retry_backoff=True, max_retries=3)
def create_job_for_expiring_rates_delay(self):
    try:
        # may insert 8k to 10k records on odd day for each fcl and air
        fcl_freight_expiring_rates_scheduler()
        air_freight_expiring_rates_scheduler()
        haulage_freight_expiring_rates_scheduler()
        
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)


@celery.task(bind=True, max_retries=3, retry_backoff=True)
def create_job_for_critical_port_pairs_delay(self):
    try:
        fcl_freight_critical_port_pairs_scheduler()
        air_freight_critical_port_pairs_scheduler()
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)
        
@celery.task(bind = True, max_retries=5, retry_backoff = True)
def send_notifications_to_supply_agents_local_feedback(self, object):
    try:
        object.send_notifications_to_supply_agents()
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)
        
@celery.task(bind=True, max_retries=1, retry_backoff=True)
def update_spot_search_delay(self, data):
    try:
        return spot_search.update_spot_search(data)
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)