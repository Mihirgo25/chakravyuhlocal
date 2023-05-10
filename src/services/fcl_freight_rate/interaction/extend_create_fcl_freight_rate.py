from params import *
from peewee import *
from services.fcl_freight_rate.helpers.fcl_freight_rate_cluster_helpers import *
from micro_services.client import *

def extend_create_fcl_freight_rate_data(request):
    from celery_worker import create_fcl_freight_rate_delay

    if request.get('extend_rates_for_lens'):
        request['source']= 'cogo_lens'
        request['mode'] = 'manual'
        create_fcl_freight_rate_delay.apply_async(kwargs={'request':request},queue='fcl_freight_rate')
        return {"message":"Creating rates in delay"}

    if request.get('extend_rates'):
        rate_objects = get_fcl_freight_cluster_objects(request)
        if rate_objects:
            create_extended_rate_objects(rate_objects)
            return {"message":"Creating rates in delay"}


def create_extended_rate_objects(rate_objects):
    from celery_worker import create_fcl_freight_rate_delay
    for rate_object in rate_objects:
        rate_object['source']= 'rate_extension'
        rate_object['mode'] = 'rate_extension'
        create_fcl_freight_rate_delay.apply_async(kwargs={'request':rate_object},queue='fcl_freight_rate')
