from peewee import *
from services.fcl_cfs_rate.models.fcl_cfs_rate import FclCfsRate

def find_rate_objects(request):
    query = (FclCfsRate
        .select()
        .where(
        (FclCfsRate.location_id == request.get('location_id')) ,
        (FclCfsRate.trade_type == request.get('trade_type') ),
        (FclCfsRate.container_size == request.get('container_size') ),
        (FclCfsRate.container_type == request.get('container_type') ),
        (FclCfsRate.commodity == request.get('commodity') ),
        (FclCfsRate.importer_exporter_id.in_([None, request.get('importer_exporter_id')])) ,
        (FclCfsRate.is_cfs_line_items_error_messages_present == request.get('is_cfs_line_items_error_messages_present'))
        ))
    return query

def update_platform_prices_for_other_service_providers(request):
    for rate_object in find_rate_objects(request):
        rate_object.set_platform_price()
        rate_object.set_is_best_price()
        rate_object.save()
