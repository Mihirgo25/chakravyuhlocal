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
from kombu import Exchange, Queue
from celery.schedules import crontab
from datetime import datetime,timedelta
import concurrent.futures

CELERY_CONFIG = {
    "enable_utc": False,
    "task_serializer": "pickle",
    "event_serializer": "pickle",
    "result_serializer": "pickle",
    "accept_content": ['application/json', 'application/x-python-serialize']
}

celery = Celery(__name__)
registry.enable("pickle")
celery.conf.broker_url = CELERY_REDIS_URL
celery.conf.result_backend = CELERY_REDIS_URL
celery.conf.critical_queues = [Queue('critical', Exchange('critical'), routing_key='critical',
          queue_arguments={'x-max-priority': 9})]
celery.conf.fcl_freight_rate_queues = [Queue('fcl_freight_rate', Exchange('fcl_freight_rate'), routing_key='fcl_freight_rate',
          queue_arguments={'x-max-priority': 6})]
celery.conf.low_queues = [Queue('low', Exchange('low'), routing_key='low',
          queue_arguments={'x-max-priority': 3})]
celery.conf.critical_default_priority = 9
celery.conf.fcl_freight_rate_default_priority = 6
celery.conf.low_default_priority = 3

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
        raise self.retry(exc = exc)

@celery.task(bind = True, max_retries=5, retry_backoff = True)
def delay_fcl_functions(self,fcl_object,request):
    try:
        create_freight_trend_port_pair(request)
        create_sailing_schedule_port_pair(request)
        if not FclFreightRate.select().where(FclFreightRate.service_provider_id==request["service_provider_id"], FclFreightRate.rate_not_available_entry==False).exists():
            organization.update_organization({'id':request.get("service_provider_id"), "freight_rates_added":True})

        if request.get("fcl_freight_rate_request_id"):
            delete_fcl_freight_rate_request(request)

        # fcl_object.create_trade_requirement_rate_mapping(request['procured_by_id'], request['performed_by_id'])
        get_multiple_service_objects(fcl_object)
    except Exception as exc:
        raise self.retry(exc=exc)


@celery.task(bind = True, max_retries=5, retry_backoff = True)
def create_sailing_schedule_port_pair(self,request):
    try:
        port_pair_coverage_data = {
        'origin_port_id': request["origin_main_port_id"] if request.get("origin_main_port_id") else request["origin_port_id"],
        'destination_port_id': request["destination_main_port_id"] if request.get("destination_main_port_id") else request["destination_port_id"],
        'shipping_line_id': request["shipping_line_id"]
        }
    except Exception as exc:
        self.retry(exc = exc)


def create_freight_trend_port_pair(request):
    try:
        port_pair_data = {
            'origin_port_id': request["origin_port_id"],
            'destination_port_id': request["destination_port_id"]
        }
    # common.create_freight_trend_port_pair(port_pair_data) expose
    except Exception as exc:
        raise exc

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
        self.retry(exc = exc)


@celery.task(bind = True, max_retries=5, retry_backoff = True)
def update_multiple_service_objects(self, object):
    try:
        get_multiple_service_objects(object)
    except Exception as exc:
        self.retry(exc = exc)

@celery.task(bind = True, max_retries=5, retry_backoff = True)
def send_closed_notifications_to_sales_agent_function(self, object):
    try:
        object.send_closed_notifications_to_sales_agent()
    except Exception as exc:
        self.retry(exc = exc)

@celery.task(bind = True, max_retries=5, retry_backoff = True)
def send_create_notifications_to_supply_agents_function(self, object):
    try:
        object.send_create_notifications_to_supply_agents()
    except Exception as exc:
        self.retry(exc = exc)

@celery.task(bind = True, max_retries=5, retry_backoff = True)
def send_notifications_to_supply_agents_local_request(self, object):
    try:
        object.send_notifications_to_supply_agents()
    except Exception as exc:
        self.retry(exc = exc)

@celery.task(bind = True, max_retries=5, retry_backoff = True)
def create_communication_background(self, data):
    try:
        common.create_communication(data)
    except Exception as exc:
        self.retry(exc = exc)

@celery.task(bind = True, max_retries=5, retry_backoff = True)
def send_fcl_freight_rate_task_notifications(self, task_id):
    try:
        send_fcl_freight_rate_task_notification(task_id)
    except Exception as exc:
        self.retry(exc = exc)

@celery.task(bind = True, max_retries=5, retry_backoff = True)
def send_closed_notifications_to_sales_agent_local_request(self, object):
    try:
        object.send_closed_notifications_to_sales_agent()
    except Exception as exc:
        self.retry(exc = exc)

@celery.task(bind = True, max_retries=5, retry_backoff = True)
def send_closed_notifications_to_sales_agent_free_day_request(self, object):
    try:
        object.send_closed_notifications_to_sales_agent()
    except Exception as exc:
        self.retry(exc = exc)

@celery.task(bind = True, max_retries=5, retry_backoff = True)
def send_closed_notifications_to_sales_agent_feedback(self, object):
    try:
        object.send_closed_notifications_to_sales_agent()
    except Exception as exc:
        self.retry(exc = exc)


@celery.task(bind = True, retry_backoff=True, max_retries=5)
def celery_create_fcl_freight_rate_free_day(self, request):
    try:
        return create_fcl_freight_rate_free_day(request)
    except Exception as e:
        raise self.retry(exc=e)


@celery.task(bind = True, retry_backoff=True, max_retries=5)
def celery_extend_create_fcl_freight_rate_data(self, request):
    try:
        return extend_create_fcl_freight_rate_data(request)
    except Exception as e:
        raise self.retry(exc=e)

@celery.task(bind = True, retry_backoff=True, max_retries=5)
def celery_create_fcl_freight_rate_local(self, request):
    try:
        return create_fcl_freight_rate_local(request)
    except Exception as e:
        raise self.retry(exc=e)

@celery.task(bind = True, max_retries=5, retry_backoff = True)
def bulk_operation_perform_action_functions(self, action_name,object,sourced_by_id,procured_by_id,cogo_entity_id):
    try:
        eval(f"object.perform_{action_name}_action(sourced_by_id='{sourced_by_id}',procured_by_id='{procured_by_id}',cogo_entity_id='{cogo_entity_id}')")
    except Exception as exc:
        raise self.retry(exc =exc)


@celery.task(bind = True, max_retries=5, retry_backoff = True)
def update_freight_objects_for_commodity_surcharge(self, surcharge_object):
    try:
        surcharge_object.update_freight_objects()
    except Exception as exc:
        raise self.retry(exc = exc)

@celery.task(bind = True, retry_backoff=True,max_retries=5)
def validate_and_process_rate_sheet_converted_file_delay(self, request):
    try:
        return validate_and_process_rate_sheet_converted_file(request)
    except Exception as exc:
        raise self.retry(exc = exc)

@celery.task(bind = True, retry_backoff=True,max_retries=5)
def fcl_freight_rates_to_cogo_assured(self):
    try:
        query =FclFreightRate.select(FclFreightRate.id, FclFreightRate.origin_port_id, FclFreightRate.origin_main_port_id, FclFreightRate.destination_port_id, FclFreightRate.destination_main_port_id, FclFreightRate.container_size, FclFreightRate.container_type, FclFreightRate.commodity
            ).where(FclFreightRate.updated_at > datetime.now() - timedelta(days = 1), FclFreightRate.validities != '[]', FclFreightRate.rate_not_available_entry == False, FclFreightRate.container_size << ['20', '40'])        
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
        raise self.retry(exc=exc)

def batches_query(query,limit,offset):
    return query.limit(limit).offset(offset)

def execute_query(query):
    return list(query.dicts())









# @celery.task()
# def create_fcl_freight_rate_feedback_for_prediction(result):
#     with db_cogo_lens.atomic() as transaction:
#         try:
#             for feedback in result:
#                 if "origin_country_id" not in feedback:
#                     feedback["origin_country_id"] = None
#                 if "destination_country_id" not in feedback:
#                     feedback["destination_country_id"] = None
#                 record = {
#                     "origin_port_id": feedback["origin_port_id"],
#                     "destination_port_id": feedback["destination_port_id"],
#                     "origin_country_id": feedback["origin_country_id"],
#                     "destination_country_id": feedback["destination_country_id"],
#                     "shipping_line_id": feedback["shipping_line_id"],
#                     "container_size": feedback["container_size"],
#                     "container_type": feedback["container_type"],
#                     "commodity": feedback["commodity"],
#                     "validity_start": feedback['validities'][0]["validity_start"],
#                     "validity_end": feedback['validities'][0]["validity_end"],
#                     "predicted_price_currency": "USD",
#                     "predicted_price": feedback["validities"][0]['line_items'][0]['price'] if ("validities" in feedback) and (feedback['validities']) else None,
#                     "actual_price": feedback["actual_price"] if "actual_price" in feedback else None,
#                     "actual_price_currency": feedback["actual_price_currency"] if "actual_price_currency" in feedback else None,
#                     "source" : "predicted_for_rate_cards",
#                     "creation_id" : feedback["id"],
#                     "importer_exporter_id" : feedback['importer_exporter_id']
#                 }

#                 new_rate = FclRatePredictionFeedback.create(**record)
#                 feedback['id'] = new_rate.id

#             c = CurrencyConverter(fallback_on_missing_rate=True, fallback_on_wrong_date=True)

#             for val in result:
#                 if ("predicted_price" in val) and val['predicted_price']:
#                     val["predicted_price"] = round(c.convert(val["predicted_price"], "USD", val["currency"], date=datetime.now()))
#             return result

# @celery.task()
# def update_expired_fcl_freight_rate_price():
#     from services.fcl_freight_rate.helpers.get_expired_rows import get_expired_fcl_freight_rates
#     from services.fcl_freight_rate.interaction.update_expired_fcl_freight_rates import update_expired_fcl_freight_rate_platform_prices
#     ides = get_expired_fcl_freight_rates()
#     for req in ides:
#         req['procured_by_id'] = "d862bb07-02fb-4adc-ae20-d6e0bda7b9c1"
#         req['sourced_by_id'] = "7f6f97fd-c17b-4760-a09f-d70b6ad963e8"
#         req['performed_by_id'] = "039a0141-e6f3-43b0-9c51-144b22b9fc84"
#         req['schedule_type'] = "transhipment"
#         req['payment_term'] = "prepaid"
#         update_expired_fcl_freight_rate_platform_prices(req)
# celery.conf.beat_schedule = {
#     'update_expired_fcl_freight_rate_price': {
#         'task': 'celery_worker.update_expired_fcl_freight_rate_price',
#         'schedule': crontab(minute=0,hour=0)
#     }
# }
# celery.start
