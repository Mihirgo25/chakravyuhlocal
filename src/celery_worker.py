from celery import Celery
from kombu.serialization import registry
from configs.env import *
from configs.fcl_freight_rate_constants import DEFAULT_RATE_TYPE
from micro_services.client import organization, common
from services.fcl_freight_rate.interaction.send_fcl_freight_rate_task_notification import send_fcl_freight_rate_task_notification
from services.fcl_freight_rate.helpers.get_multiple_service_objects import get_multiple_service_objects
from services.rate_sheet.interactions.validate_and_process_rate_sheet_converted_file import validate_and_process_rate_sheet_converted_file
from services.fcl_freight_rate.interaction.extend_create_fcl_freight_rate import extend_create_fcl_freight_rate_data
from services.fcl_freight_rate.interaction.create_fcl_freight_rate import create_fcl_freight_rate_data
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from services.fcl_customs_rate.models.fcl_customs_rate import FclCustomsRate
from services.fcl_cfs_rate.models.fcl_cfs_rate import FclCfsRate
from services.fcl_freight_rate.interaction.delete_fcl_freight_rate_request import delete_fcl_freight_rate_request
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_free_day import create_fcl_freight_rate_free_day
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_local import create_fcl_freight_rate_local
from services.ftl_freight_rate.scheduler.fuel_scheduler import fuel_scheduler
from services.haulage_freight_rate.schedulers.electricity_price_scheduler import electricity_price_scheduler
from services.fcl_freight_rate.interaction.add_local_rates_on_country import add_local_rates_on_country
from kombu import Exchange, Queue
from celery.schedules import crontab
from datetime import datetime,timedelta
import concurrent.futures
from services.envision.interaction.create_fcl_freight_rate_prediction_feedback import create_fcl_freight_rate_prediction_feedback
from services.fcl_freight_rate.interaction.update_cogo_assured_fcl_freight_rate_validities import update_cogo_assured_fcl_freight_rate_validities
from services.fcl_freight_rate.interaction.update_fcl_rates_to_cogo_assured import update_fcl_rates_to_cogo_assured
from services.fcl_freight_rate.interaction.update_fcl_freight_rate_request import update_fcl_freight_rate_request
from services.chakravyuh.interaction.get_air_invoice_estimation_prediction import invoice_rates_updation
from services.fcl_customs_rate.interaction.update_fcl_customs_rate_platform_prices import update_fcl_customs_rate_platform_prices
from services.fcl_cfs_rate.interaction.update_fcl_cfs_rate_platform_prices import update_fcl_cfs_rate_platform_prices 
from services.extensions.interactions.create_freight_look_rates import create_air_freight_rate_api
from services.air_freight_rate.interactions.create_draft_air_freight_rate import create_draft_air_freight_rate
from database.rails_db import get_past_cost_booking_data
from services.fcl_freight_rate.interaction.update_fcl_freight_rate_feedback import update_fcl_freight_rate_feedback
from services.fcl_customs_rate.interaction.create_fcl_customs_rate import create_fcl_customs_rate
from services.fcl_customs_rate.helpers import update_organization_fcl_customs
from services.fcl_cfs_rate.helpers import update_organization_fcl_cfs
from services.air_freight_rate.interactions.update_air_freight_rate_request import update_air_freight_rate_request
from services.envision.interaction.create_air_freight_rate_prediction_feedback import create_air_freight_rate_feedback
from services.air_freight_rate.interactions.create_air_freight_rate_local import create_air_freight_rate_local
from services.air_freight_rate.interactions.create_air_freight_rate import create_air_freight_rate
from services.air_freight_rate.interactions.create_air_freight_rate_surcharge import create_air_freight_rate_surcharge
from services.air_freight_rate.helpers.create_saas_air_schedule_helper import create_saas_air_schedule_airport_pair
from services.air_freight_rate.interactions.send_air_freight_rate_task_notification import send_air_freight_rate_task_notification
from services.air_freight_rate.workers.send_air_freight_local_charges_update_reminder_notification import send_air_freight_local_charges_update_reminder_notification
from services.air_freight_rate.workers.send_expired_air_freight_rate_notification import send_expired_air_freight_rate_notification
from services.air_freight_rate.workers.send_near_expiry_air_freight_rate_notification import send_near_expiry_air_freight_rate_notification
from services.air_freight_rate.helpers.air_freight_rate_card_helper import get_rate_from_cargo_ai
from services.extensions.interactions.create_freight_look_surcharge_rates import create_surcharge_rate_api
from services.air_freight_rate.estimators.relate_airlines import RelateAirline
# Rate Producers

from services.chakravyuh.producer_vyuhs.fcl_freight import FclFreightVyuh as FclFreightVyuhProducer
from services.chakravyuh.producer_vyuhs.air_freight import AirFreightVyuh as AirFreightVyuhProducer

# Dynamic Pricing

from services.chakravyuh.setters.fcl_freight import FclFreightVyuh as FclFreightVyuhSetter
from services.chakravyuh.setters.fcl_booking_invoice import FclBookingVyuh as FclBookingVyuhSetters
from services.chakravyuh.setters.air_freight import AirFreightVyuh as AirFreightVyuhSetter

# Brahmastra
from services.bramhastra.brahmastra import Brahmastra
from services.bramhastra.interactions.apply_fcl_freight_rate_statistic import apply_fcl_freight_rate_statistic
from services.bramhastra.interactions.apply_fcl_freight_rate_feedback import apply_feedback_fcl_freight_rate_statistic
from services.bramhastra.interactions.apply_fcl_freight_rate_request_statistic import apply_fcl_freight_rate_request_statistic

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
celery.conf.critical_queues = [Queue('critical', Exchange('critical'), routing_key='critical',
          queue_arguments={'x-max-priority': 6})]
celery.conf.communication_queues = [Queue('communication', Exchange('communication'), routing_key='communication',
          queue_arguments={'x-max-priority': 6})]
celery.conf.bulk_operation_queues = [Queue('bulk_operations', Exchange('bulk_operations'), routing_key='bulk_operations',
          queue_arguments={'x-max-priority': 4})]
celery.conf.statistics_operations = [Queue('statistics', Exchange('statistics'), routing_key='statistics',
          queue_arguments={'x-max-priority':4})]
celery.conf.fcl_freight_rate_queues = [Queue('fcl_freight_rate', Exchange('fcl_freight_rate'), routing_key='fcl_freight_rate',
          queue_arguments={'x-max-priority': 2})]
celery.conf.low_queues = [Queue('low', Exchange('low'), routing_key='low',
          queue_arguments={'x-max-priority': 2})]

celery.conf.update(**CELERY_CONFIG)
celery.conf.beat_schedule = {
    'fcl_freigh_rates_to_cogo_assured': {
        'task': 'celery_worker.fcl_freight_rates_to_cogo_assured',
        'schedule': crontab(minute=00,hour=00),
        'options': {'queue' : 'fcl_freight_rate'}
        },
    # 'update_cogo_assured_fcl_freight_rates': {
    #     'task': 'celery_worker.update_cogo_assured_fcl_freight_rates',
    #     'schedule': crontab(minute=30, hour=18),
    #     'options': { 'queue': 'fcl_freight_rate' }
    #     },
    'process_fuel_data_delays': {
        'task': 'celery_worker.process_fuel_data_delay',
        'schedule': crontab(minute=00,hour=21),
        'options': {'queue' : 'fcl_freight_rate'}
        },
    # 'adjust_air_freight_dynamic_pricing':{
    #     'task': 'celery_worker.adjust_air_freight_dynamic_pricing',
    #     'schedule': crontab(minute=00,hour=00),
    #     'options': {'queue' : 'fcl_freight_rate'}
    # },
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
    'send_near_expiry_air_freight_rate_notification':{
        'task': 'celery_worker.send_near_expiry_air_freight_rate_notification_in_delay',
        'schedule': crontab(minute=30,hour=5),
        'options': {'queue' : 'low'}
    },
    'send_expired_air_freight_rate_notification':{
        'task': 'celery_worker.send_expired_air_freight_rate_notification_in_delay',
        'schedule': crontab(minute=30,hour=5),
        'options': {'queue' : 'low'}
    },
    'send_air_freight_local_charges_update_reminder_notification':{
        'task': 'celery_worker.send_air_freight_local_charges_update_reminder_notification_in_delay',
        'schedule': crontab(minute=30,hour=5,day_of_month = '1'),
        'options': {'queue': 'low'}
    },
    'adjust_air_freight_rate_airline_factors':{
        'task': 'celery_worker.air_freight_airline_factors_in_delay',
        'schedule': crontab(hour=5, minute=30, day_of_week='sun'),
        'options': {'queue': 'low'}
    },
    'arjun_in_delay':{
        'task': 'celery_worker.arjun_in_delay',
        'schedule': crontab(hour='*/2'),
        'options': {'queue': 'critical'}
    },
    'cache_data_worker_in_delay':{
        'task': 'celery_worker.cache_data_worker_in_delay',
        'schedule': crontab(hour=12, minute=0),
        'options': {'queue': 'low'}
    },
    'fcl_extended_object_worker_in_delay':{
        'task': 'celery_worker.fcl_extended_object_worker_in_delay',
        'schedule': crontab(hour=12, minute=0),
        'options': {'queue': 'statistics'}
    }
}
celery.autodiscover_tasks(['services.haulage_freight_rate.haulage_celery_worker'], force=True)


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
def create_fcl_freight_rate_delay(self, request):
    try:
        return create_fcl_freight_rate_data(request)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, max_retries=5, retry_backoff = True)
def delay_fcl_functions(self, request):
    try:
        if not FclFreightRate.select().where(FclFreightRate.service_provider_id==request["service_provider_id"], FclFreightRate.rate_not_available_entry==False, FclFreightRate.rate_type == DEFAULT_RATE_TYPE).exists():
            organization.update_organization({'id':request.get("service_provider_id"), "freight_rates_added":True})

        if request.get("fcl_freight_rate_request_id"):
            delete_fcl_freight_rate_request(request)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)



@celery.task(bind = True, max_retries=5, retry_backoff = True)
def fcl_freight_local_data_updation(self, request):
    try:
        params = {
        'performed_by_id': request['performed_by_id'],
        'organization_id': request['service_provider_id'],
        'port_id': request['port_id'],
        'trade_type': request['trade_type']
        }
        organization.create_organization_serviceable_port(params)
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
def send_fcl_freight_rate_task_notifications(self, task_id):
    try:
        send_fcl_freight_rate_task_notification(task_id)
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

@celery.task(bind = True, retry_backoff=True, max_retries=5)
def celery_create_fcl_freight_rate_free_day(self, request):
    try:
        return create_fcl_freight_rate_free_day(request)
    except Exception as e:
        if type(e).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= e)


@celery.task(bind = True, retry_backoff=True, max_retries=5)
def celery_extend_create_fcl_freight_rate_data(self, request):
    try:
        return extend_create_fcl_freight_rate_data(request)
    except Exception as e:
        if type(e).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= e)

@celery.task(bind = True, retry_backoff=True, max_retries=5)
def celery_create_fcl_freight_rate_local(self, request):
    try:
        return create_fcl_freight_rate_local(request)
    except Exception as e:
        if type(e).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= e)

@celery.task(bind = True, max_retries=5, retry_backoff = True)
def bulk_operation_perform_action_functions(self, action_name,object,sourced_by_id,procured_by_id,cogo_entity_id):
    eval_string = f"object.perform_{action_name}_action(sourced_by_id='{sourced_by_id}',procured_by_id='{procured_by_id}')"
    if cogo_entity_id:
        eval_string = f"object.perform_{action_name}_action(sourced_by_id='{sourced_by_id}',procured_by_id='{procured_by_id}',cogo_entity_id='{cogo_entity_id}')"
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

@celery.task(bind = True, retry_backoff=True,max_retries=1)
def fcl_freight_rates_to_cogo_assured(self):
    try:
        query =FclFreightRate.select(FclFreightRate.id, FclFreightRate.origin_port_id, FclFreightRate.origin_main_port_id, FclFreightRate.destination_port_id, FclFreightRate.destination_main_port_id, FclFreightRate.container_size, FclFreightRate.container_type, FclFreightRate.commodity
            ).where(FclFreightRate.mode != "predicted", FclFreightRate.updated_at > datetime.now() - timedelta(days = 1), FclFreightRate.validities != '[]', FclFreightRate.rate_not_available_entry == False, FclFreightRate.container_size << ['20', '40'], FclFreightRate.rate_type == DEFAULT_RATE_TYPE)
        total_count = query.count()
        batches = int(total_count/5000)
        last_batch = total_count%5000
        offset =0
        limit =5000
        queries =[]
        for each in range(0,batches):
            queries.append(batches_query(query,limit,offset))
            offset = offset+limit
        if last_batch:
            queries.append(batches_query(query,last_batch,offset))

        query_result = []
        with concurrent.futures.ThreadPoolExecutor(max_workers = 4) as executor:
            futures = [executor.submit(execute_query, query) for query in queries]

            for i in range(0,len(futures)):
                result = futures[i].result()
                query_result.extend(result)
        date = datetime.now() - timedelta(days = 1)
        for each in query_result:
            data ={"origin_location_id": each['origin_port_id'], "origin_port_id": each['origin_main_port_id'], "destination_location_id": each['destination_port_id'], "destination_port_id": each['destination_main_port_id'], "container_size": each["container_size"], "container_type": each["container_type"], "commodity": each['commodity'], "fcl_rates_updated_date": date}
            common.fcl_freight_rates_to_cogo_assured(data)
    except Exception as exc:
        pass

def batches_query(query,limit,offset):
    return query.limit(limit).offset(offset)

def execute_query(query):
    return list(query.dicts())

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
def create_fcl_freight_rate_feedback_for_prediction(self, result):
    try:
        create_fcl_freight_rate_prediction_feedback(result)
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

@celery.task(bind=True, retry_backoff=True,max_retries=3)
def transform_air_dynamic_pricing(self, new_rate, affected_transformation, new):
    try:
        air_freight_vyuh = AirFreightVyuhSetter(new_rate=new_rate)
        air_freight_vyuh.adjust_price_for_tranformation(affected_transformation=affected_transformation, new=new)
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

@celery.task(bind = True, retry_backoff = True, max_retries = 3)
def create_country_wise_locals_in_delay(self, request):
    try:
        add_local_rates_on_country(request)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)        

@celery.task(bind=True, retry_backoff=True, max_retries=1)
def update_cogo_assured_fcl_freight_rates(self):
    batch_size = 5000
    cogo_assured_rates = FclFreightRate.select().where(FclFreightRate.rate_type == 'cogo_assured')
    total_size = cogo_assured_rates.count()
    
    for batch in range(0, total_size, batch_size):
        batched_rates = cogo_assured_rates.limit(batch_size).offset(batch)
        if not batched_rates.exists():
            break
        
        batch_rates = list(batched_rates.dict())
        for rate in batched_rates:
            update_cogo_assured_fcl_freight_rate_validities(rate)

@celery.task(bind = True, retry_backoff=True,max_retries=5)
def update_fcl_freight_rate_request_in_delay(self, request):
    try:
        update_fcl_freight_rate_request(request)
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
@celery.task(bind = True, retry_backoff=True,max_retries=5)
def update_air_freight_rate_details_delay(self, request):
    try:
        update_air_freight_rate_request(request)
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
def create_air_freight_rate_delay(self, request):
    try:
        # return create_draft_air_freight_rate(request)
        return create_air_freight_rate(request)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, max_retries=5, retry_backoff = True)
def adjust_air_freight_dynamic_pricing(self):
    try:
        # return True
        return invoice_rates_updation()
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, retry_backoff=True, max_retries=1)
def process_freight_look_rates(self, rate, locations):
    try:
        return create_air_freight_rate_api(rate=rate, locations=locations)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, retry_backoff=True, max_retries=5)
def create_fcl_customs_rate_delay(self, request):
    try:
        return create_fcl_customs_rate(request)
    except Exception as e:
        if type(e).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= e)

@celery.task(bind = True, max_retries=5, retry_backoff = True)
def update_fcl_customs_rate_platform_prices_delay(self, request):
    try:
        update_fcl_customs_rate_platform_prices(request)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, max_retries=5, retry_backoff = True)
def update_fcl_cfs_rate_platform_prices_delay(self, request):
    try:
        update_fcl_cfs_rate_platform_prices(request)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, max_retries=5, retry_backoff = True)
def fcl_customs_functions_delay(self,fcl_customs_object,request):
    try:
        update_organization_fcl_customs(request)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, max_retries=5, retry_backoff = True)
def fcl_cfs_functions_delay(self,fcl_cfs_object,request):
    try:
        update_organization_fcl_cfs(request)
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

@celery.task(bind = True, max_retries=5, retry_backoff = True)
def send_notifications_to_supply_agents_cfs_request_delay(self, object):
    try:
        object.send_notifications_to_supply_agents()
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, retry_backoff = True,max_retries=1)
def air_freight_rate_prediction_feedback_delay(self, result):
    try:
        create_air_freight_rate_feedback(result)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)
        
@celery.task(bind = True, max_retries=5, retry_backoff = True)
def create_saas_air_schedule_airport_pair_delay (self,air_object,request):
    try:
        create_saas_air_schedule_airport_pair(air_object,request)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)
        
@celery.task(bind = True, retry_backoff = True, max_retries=5)
def create_air_freight_rate_local_delay(self, request):
    try:
        return create_air_freight_rate_local(request)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)
        
@celery.task(bind = True,retry_backoff = True, max_retries=5)
def create_air_freight_rate_freight_delay(self, request):
    try:
        return create_air_freight_rate(request)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)
    
@celery.task(bind = True, retry_backoff = True, max_retries=5)
def create_air_freight_rate_surcharge_delay(self, request):
    try:
        return create_air_freight_rate_surcharge(request)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)


@celery.task(bind = True, retry_backoff=True,max_retries=3)
def extend_air_freight_rates(self, rate, source = 'rate_extension'):
    try:
        air_freight_vyuh = AirFreightVyuhProducer(rate=rate)
        air_freight_vyuh.extend_rate(source=source)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, retry_backoff=True,max_retries=3)
def update_fcl_freight_rate_feedback_in_delay(self, request):
    try:
        update_fcl_freight_rate_feedback(request)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, retry_backoff=True,max_retries=3)
def send_air_freight_rate_task_notification_in_delay(self,task_id):
    try:
        send_air_freight_rate_task_notification(task_id)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)
        
@celery.task(bind = True, retry_backoff=True,max_retries=3)
def get_rate_from_cargo_ai_in_delay(self,air_freight_rate,feedback,performed_by_id):
    try:
        get_rate_from_cargo_ai(air_freight_rate,feedback,performed_by_id)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)
        
@celery.task(bind = True, retry_backoff=True,max_retries=3)
def send_air_freight_local_charges_update_reminder_notification_in_delay(self):
    try:
        send_air_freight_local_charges_update_reminder_notification()
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, retry_backoff=True,max_retries=3)
def send_expired_air_freight_rate_notification_in_delay(self):
    try:
        send_expired_air_freight_rate_notification()
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, retry_backoff=True,max_retries=3)
def send_near_expiry_air_freight_rate_notification_in_delay(self):
    try:
        send_near_expiry_air_freight_rate_notification()
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

@celery.task(bind = True,retry_backoff=True,max_retries=3)
def extend_air_freight_rates_in_delay(self, rate):
    try:
        air_freight_vyuh = AirFreightVyuhProducer(rate=rate)
        air_freight_vyuh.extend_rate()
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc) 

@celery.task(bind = True,retry_backoff=True,max_retries=3)
def air_freight_airline_factors_in_delay(self):
    try:
        relate_ailine = RelateAirline()
        relate_ailine.relate_airlines()
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc) 

@celery.task(bind=True,retry_backoff=True,max_retries=5)
def arjun_in_delay(self):
    # using this until we get all queries right
    try:
        brahmastra=Brahmastra()
        brahmastra.use(arjun = True)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)
        
@celery.task(bind=True,retry_backoff=True,max_retries=5)
def cache_data_worker_in_delay(self):
    try:
        # this caches statistics csv into redis for huge data
        from services.bramhastra.workers.cache_data_worker import FclCacheData
        FclCacheData().set_all_time_accuracy_chart()
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)
        
        
@celery.task(bind=True,retry_backoff=True,max_retries=5)
def fcl_extended_object_worker_in_delay(self):
    try:
        # this sets parent_rate_id for rates created via extensions
        from services.bramhastra.workers.fcl_extended_object_worker import FclExtendObjectWorker
        FclExtendObjectWorker().execute()
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)
        
@celery.task(bind = True, retry_backoff=True,max_retries=5)
def apply_fcl_freight_rate_statistic_delay(self,action,params):
    from services.bramhastra.request_params import ApplyFclFreightRateStatistic
    try:
        return apply_fcl_freight_rate_statistic(ApplyFclFreightRateStatistic(action = action,params = params))
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, retry_backoff=True,max_retries=5)
def apply_feedback_fcl_freight_rate_statistic_delay(self,action,params):
    from services.bramhastra.request_params import ApplyFeedbackFclFreightRateStatistics
    try:
        return apply_feedback_fcl_freight_rate_statistic(ApplyFeedbackFclFreightRateStatistics(action = action,params = params))
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)
     
        
@celery.task(bind = True, retry_backoff=True,max_retries=5)
def apply_fcl_freight_rate_request_statistic_delay(self,action,params):
    from services.bramhastra.request_params import ApplyFclFreightRateRequestStatistic
    try:
        return apply_fcl_freight_rate_request_statistic(ApplyFclFreightRateRequestStatistic(action = action,params = params))
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)