from celery import Celery
import os
from configs.env import *
from micro_services.client import organization, common
from services.fcl_freight_rate.models.fcl_freight_rate_request import FclFreightRateRequest
from services.fcl_freight_rate.models.fcl_freight_rate_local_request import FclFreightRateLocalRequest
from services.fcl_freight_rate.models.fcl_freight_rate_feedback import FclFreightRateFeedback
from services.fcl_freight_rate.models.fcl_freight_rate_free_day_request import FclFreightRateFreeDayRequest
from services.fcl_freight_rate.interaction.send_fcl_freight_rate_task_notification import send_fcl_freight_rate_task_notification
from services.fcl_freight_rate.helpers.get_multiple_service_objects import get_multiple_service_objects
from libs.locations import list_locations

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
    from services.fcl_freight_rate.interaction.create_fcl_freight_rate import create_fcl_freight_rate
    return create_fcl_freight_rate(request)

@celery.task(max_retries=10)
def delay_fcl_functions(fcl_object,request):
    from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
    from services.fcl_freight_rate.helpers.get_multiple_service_objects import get_multiple_service_objects
    from services.fcl_freight_rate.interaction.delete_fcl_freight_rate_request import delete_fcl_freight_rate_request
    print(create_freight_trend_port_pair(request))
    create_sailing_schedule_port_pair(request)
    if not FclFreightRate.select().where(FclFreightRate.service_provider_id==request["service_provider_id"], FclFreightRate.rate_not_available_entry==False).exists():
        organization.update_organization({'id':request.get("service_provider_id"), "freight_rates_added":True})

    if request.get("fcl_freight_rate_request_id"):
        delete_fcl_freight_rate_request(request)
    
    # fcl_object.create_trade_requirement_rate_mapping(request['procured_by_id'], request['performed_by_id'])

    
    get_multiple_service_objects(fcl_object)


    fcl_object.update_special_attributes()

    fcl_object.update_local_references()

    fcl_object.update_platform_prices_for_other_service_providers()


@celery.task()
def create_sailing_schedule_port_pair(request):
    port_pair_coverage_data = {
    'origin_port_id': request["origin_main_port_id"] if request.get("origin_main_port_id") else request["origin_port_id"],
    'destination_port_id': request["destination_main_port_id"] if request.get("destination_main_port_id") else request["destination_port_id"],
    'shipping_line_id': request["shipping_line_id"]
    }
    common.create_sailing_schedule_port_pair_coverage(port_pair_coverage_data)

def create_freight_trend_port_pair(request):
    port_pair_data = {
        'origin_port_id': request["origin_port_id"],
        'destination_port_id': request["destination_port_id"]
    }

  
  # common.create_freight_trend_port_pair(port_pair_data) expose

@celery.task()
def fcl_freight_local_data_updation(local_object,request):
  from services.fcl_freight_rate.interaction.create_fcl_freight_rate_local import local_updations

    
  update_multiple_service_objects.apply_async(kwargs={"object":local_object},queue='low')

  local_updations(local_object,request)


@celery.task()
def update_multiple_service_objects(object):
  get_multiple_service_objects(object)

@celery.task()
def send_closed_notifications_to_sales_agent_function(object):
    object.send_closed_notifications_to_sales_agent()

@celery.task()
def send_create_notifications_to_supply_agents_function(object):
    object.send_create_notifications_to_supply_agents()

@celery.task()
def send_notifications_to_supply_agents_local_request(object):
    object.send_notifications_to_supply_agents()

@celery.task()
def create_communication_background(data):
    common.create_communication(data)

@celery.task()
def send_fcl_freight_rate_task_notification(task_id):
    send_fcl_freight_rate_task_notification(task_id)


@celery.task()
def send_closed_notifications_to_sales_agent_local_request(object):
    object.send_closed_notifications_to_sales_agent()

@celery.task()
def send_closed_notifications_to_sales_agent_free_day_request(object):
    object.send_closed_notifications_to_sales_agent()

@celery.task()
def send_closed_notifications_to_sales_agent_feedback(object):
    object.send_closed_notifications_to_sales_agent()




@celery.task()
def bulk_operation_perform_action_functions(action_name,object,sourced_by_id,procured_by_id,cogo_entity_id):
    eval(f"object.perform_{action_name}_action(sourced_by_id='{sourced_by_id}',procured_by_id='{procured_by_id}',cogo_entity_id={cogo_entity_id})")


@celery.task()
def update_freight_objects_for_commodity_surcharge(surcharge_object):

    surcharge_object.update_freight_objects()






