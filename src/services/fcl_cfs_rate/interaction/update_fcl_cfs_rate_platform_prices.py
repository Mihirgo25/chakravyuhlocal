from peewee import *
from services.fcl_cfs_rate.models.fcl_cfs_rate import FclCfsRate

def update_fcl_cfs_rate_platform_prices(request):
    
    query = (FclCfsRate
        .select()
        .where(
        (FclCfsRate.location_id == request.get('location_id')) ,
        (FclCfsRate.trade_type == request.get('trade_type') ),
        (FclCfsRate.container_size == request.get('container_size') ),
        (FclCfsRate.container_type == request.get('container_type') ),
        (FclCfsRate.commodity == request.get('commodity') ),
        (FclCfsRate.cargo_handling_type == request.get('cargo_handling_type')),
        ((FclCfsRate.importer_exporter_id == request.get('importer_exporter_id')) | (FclCfsRate.importer_exporter_id.is_null(True))),
        (FclCfsRate.is_cfs_line_items_error_messages_present == request.get('is_cfs_line_items_error_messages_present'))
        )).execute()
    
    for rate_object in query:
        rate_object.set_platform_price()
        rate_object.set_is_best_price()
        rate_object.save()
        
    return True