from datetime import date
from configs.fcl_freight_rate_constants import DEFAULT_RATE_TYPE

def update_fcl_freight_rate_platform_prices(request):
    from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate

    freight_objects = FclFreightRate.select().where(
    FclFreightRate.origin_port_id == request.get('origin_port_id'),
    FclFreightRate.origin_main_port_id == request['origin_main_port_id'],
    FclFreightRate.destination_port_id == request['destination_port_id'],
    FclFreightRate.destination_main_port_id == request['destination_main_port_id'],
    FclFreightRate.container_size == request['container_size'],
    FclFreightRate.container_type == request['container_type'],
    FclFreightRate.commodity == request['commodity'],
    FclFreightRate.shipping_line_id == request['shipping_line_id'],
    FclFreightRate.importer_exporter_id == request['importer_exporter_id'],
    FclFreightRate.last_rate_available_date >= date.today(),
    FclFreightRate.rate_type == DEFAULT_RATE_TYPE
    )

    if 'origin_main_port_id' in request:
        freight_objects = freight_objects.where(FclFreightRate.origin_main_port_id == request['origin_main_port_id'])
    else:
        freight_objects = freight_objects.where(FclFreightRate.origin_main_port_id == None)
    if 'destination_port_id' in request:
        freight_objects = freight_objects.where(FclFreightRate.destination_port_id == request['destination_port_id'])
    else:
        freight_objects = freight_objects.where(FclFreightRate.destination_port_id == None)
    
    if 'importer_exporter_id' in request:
        freight_objects = freight_objects.where(FclFreightRate.importer_exporter_id == request['importer_exporter_id'])
    else:
        freight_objects = freight_objects.where(FclFreightRate.importer_exporter_id == None)
    
    freight_objects = freight_objects.execute()

    for freight in freight_objects:
        freight.set_platform_prices()
        freight.set_is_best_price()
        freight.save()