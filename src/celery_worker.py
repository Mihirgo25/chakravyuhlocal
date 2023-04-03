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



CELERY_CONFIG = {
    "enable_utc": True,
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

        fcl_object.create_trade_requirement_rate_mapping(request['procured_by_id'], request['performed_by_id'])
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
