from params import *
from peewee import *
from micro_services.client import *
from services.fcl_freight_rate.helpers.fcl_freight_rate_cluster_helpers import *
from services.ftl_freight_rate.interactions.create_ftl_freight_rate import create_ftl_freight_rate
from services.ftl_freight_rate.models.ftl_freight_rate import FtlFreightRate
from services.ftl_freight_rate.ftl_celery_worker import create_ftl_freight_rate_delay

def extend_ftl_freight_rate(request):
    
    params = {
        'rate_sheet_id': request.get('rate_sheet_id'),
        'origin_location_id': request.get('origin_location_id'),
        'destination_location_id': request.get('destination_location_id'),
        'truck_type': request.get('truck_type'),
        'commodity': request.get('commodity'),
        'importer_exporter_id': request.get('importer_exporter_id'),
        'service_provider_id': request.get('service_provider_id'),
        'performed_by_id': request.get('performed_by_id'),
        'procured_by_id': request.get('procured_by_id'),
        'sourced_by_id': request.get('sourced_by_id'),
        'validity_start': request.get('validity_start'),
        'validity_end': request.get('validity_end'),
        'truck_body_type': request.get('truck_body_type'),
        'trip_type': request.get('trip_type'),
        'transit_time': request.get('transit_time'),
        'detention_free_time': request.get('detention_free_time'),
        'line_items': request.get('line_items'),
        'ftl_freight_rate_request_id': request.get('ftl_freight_rate_request_id')
    }
    
    create_ftl_freight_rate_delay.apply_async(
        kwargs={
            'request': params
        },queue='low'
    )
    
    return {
        "message": "Creating in delay",
    }