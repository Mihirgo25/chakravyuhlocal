
from services.ftl_freight_rate.models.ftl_freight_rate import FtlFreightRate
def update_ftl_freight_rate_platform_prices(request):
    
    ftl_freight_objects = find_rate_objects(request)
    
    for freight in ftl_freight_objects:
        freight.set_platform_price()
        freight.set_is_best_price()
        freight.save()
    
def find_rate_objects(request):
    ftl_freight_rate_objects = FtlFreightRate.select().where(FtlFreightRate.origin_location_id == request.get('origin_location_id'),FtlFreightRate.destination_location_id == request.get('destination_location_id'),FtlFreightRate.truck_type == request.get('truck_type'),FtlFreightRate.commodity == request.get('commodity'), (FtlFreightRate.importer_exporter_id == request.get('importer_exporter_id')) | (FtlFreightRate.importer_exporter_id.is_null(True)),FtlFreightRate.is_line_items_error_messages_present == False).execute()
    return ftl_freight_rate_objects