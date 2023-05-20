from celery import Celery
from kombu.serialization import registry
from configs.env import *
from micro_services.client import organization, common
from services.fcl_freight_rate.interaction.send_fcl_freight_rate_task_notification import send_fcl_freight_rate_task_notification
from services.fcl_freight_rate.helpers.get_multiple_service_objects import get_multiple_service_objects
from services.rate_sheet.interactions.validate_and_process_rate_sheet_converted_file import validate_and_process_rate_sheet_converted_file
from services.fcl_freight_rate.interaction.extend_create_fcl_freight_rate import extend_create_fcl_freight_rate_data
from services.fcl_freight_rate.interaction.create_fcl_freight_rate import create_fcl_freight_rate_data
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.interaction.delete_fcl_freight_rate_request import delete_fcl_freight_rate_request
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_free_day import create_fcl_freight_rate_free_day
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_local import create_fcl_freight_rate_local
from services.chakravyuh.interaction.get_local_rates_from_vyuh import add_local_rates_on_country
from kombu import Exchange, Queue
from celery.schedules import crontab
from datetime import datetime,timedelta
import concurrent.futures
from services.envision.interaction.create_fcl_freight_rate_prediction_feedback import create_fcl_freight_rate_prediction_feedback

# Rate Producers

from services.chakravyuh.producer_vyuhs.fcl_freight import FclFreightVyuh as FclFreightVyuhProducer

# Dynamic Pricing

from services.chakravyuh.setters.fcl_freight import FclFreightVyuh as FclFreightVyuhSetter

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
          queue_arguments={'x-max-priority': 4})]
celery.conf.communication_queues = [Queue('communication', Exchange('communication'), routing_key='communication',
          queue_arguments={'x-max-priority': 4})]
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
        }
}


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
def delay_fcl_functions(self,fcl_object,request):
    try:
        if not FclFreightRate.select().where(FclFreightRate.service_provider_id==request["service_provider_id"], FclFreightRate.rate_not_available_entry==False).exists():
            organization.update_organization({'id':request.get("service_provider_id"), "freight_rates_added":True})

        if request.get("fcl_freight_rate_request_id"):
            delete_fcl_freight_rate_request(request)

        get_multiple_service_objects(fcl_object)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)



@celery.task(bind = True, max_retries=5, retry_backoff = True)
def fcl_freight_local_data_updation(self, local_object,request):
    try:
        update_multiple_service_objects.apply_async(kwargs={"object":local_object},queue='low')
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
    try:
        eval(f"object.perform_{action_name}_action(sourced_by_id='{sourced_by_id}',procured_by_id='{procured_by_id}',cogo_entity_id='{cogo_entity_id}')")
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
def fcl_freight_rates_to_cogo_assured(self):
    try:
        query =FclFreightRate.select(FclFreightRate.id, FclFreightRate.origin_port_id, FclFreightRate.origin_main_port_id, FclFreightRate.destination_port_id, FclFreightRate.destination_main_port_id, FclFreightRate.container_size, FclFreightRate.container_type, FclFreightRate.commodity
            ).where(FclFreightRate.mode != "predicted", FclFreightRate.updated_at > datetime.now() - timedelta(days = 1), FclFreightRate.validities != '[]', FclFreightRate.rate_not_available_entry == False, FclFreightRate.container_size << ['20', '40'])
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
