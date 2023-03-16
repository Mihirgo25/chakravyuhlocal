from celery import Celery
import os
import time
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


@celery.task()
def create_fcl_freight_rate_delay(request):
    from rails_client import client
    from services.fcl_freight_rate.interaction.create_fcl_freight_rate import create_fcl_freight_rate
    return create_fcl_freight_rate(request)

@celery.task()
def delay_fcl_functions(fcl_object,request):
    from rails_client import client
    from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
    from services.fcl_freight_rate.helpers.get_multuple_service_objects import get_multiple_service_objects
    from services.fcl_freight_rate.interaction.delete_fcl_freight_rate_request import delete_fcl_freight_rate_request
    client.initialize_client()
    create_freight_trend_port_pair(request)
    create_sailing_schedule_port_pair(request)
    if not FclFreightRate.select().where(FclFreightRate.service_provider_id==request["service_provider_id"], FclFreightRate.rate_not_available_entry==False).exists():
        client.ruby.update_organization({'id':request.get("service_provider_id"), "freight_rates_added":True})

    if request.get("fcl_freight_rate_request_id"):
        delete_fcl_freight_rate_request(request)
    
    fcl_object.create_trade_requirement_rate_mapping(request['procured_by_id'], request['performed_by_id'])
    services ={'objects':[
    {
      'name': 'operator',
      'filters': { 'id': [str(fcl_object.shipping_line_id)]},
      'fields': ['id', 'business_name', 'short_name', 'logo_url']
    },
    {
      'name': 'location', 
      'filters':{"id": list(set(list(filter(None, [str(fcl_object.origin_port_id), str(fcl_object.destination_port_id)] ))))},
      'fields': ['id', 'name', 'display_name', 'port_code', 'type', 'is_icd']
    },
    {
      'name': 'organization',
      'filters': {"id": list(set([str(fcl_object.service_provider_id), str(fcl_object.importer_exporter_id)] ))},
      'fields': ['id', 'business_name', 'short_name']
    },
    {
      'name': 'user',
      'filters': {"id": list(set([fcl_object.procured_by_id, fcl_object.sourced_by_id]  ))},
      'fields': ['id', 'name', 'email']
    }
  ]}
    
    get_multiple_service_objects(fcl_object,services)


    fcl_object.update_special_attributes()

    fcl_object.update_local_references()

    fcl_object.update_platform_prices_for_other_service_providers()


@celery.task()
def create_sailing_schedule_port_pair(request):
    from rails_client import client
    port_pair_coverage_data = {
    'origin_port_id': request["origin_main_port_id"] if request.get("origin_main_port_id") else request["origin_port_id"],
    'destination_port_id': request["destination_main_port_id"] if request.get("destination_main_port_id") else request["destination_port_id"],
    'shipping_line_id': request["shipping_line_id"]
    }
    data = client.ruby.create_sailing_schedule_port_pair_coverage(port_pair_coverage_data)
    print(data)

def create_freight_trend_port_pair(request):
    port_pair_data = {
        'origin_port_id': request["origin_port_id"],
        'destination_port_id': request["destination_port_id"]
    }

  
  # client.ruby.create_freight_trend_port_pair(port_pair_data) expose
    




