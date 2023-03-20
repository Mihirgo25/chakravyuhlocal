from datetime import date
from peewee import fn

def update_fcl_freight_rate_platform_prices(request):
    from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate

    freight_objects = FclFreightRate.select().where(
    FclFreightRate.origin_port_id == request.get('origin_port_id'),
    FclFreightRate.origin_main_port_id == request['origin_main_port_id'] if request.get('origin_main_port_id') else (FclFreightRate.id.is_null(False)),
    FclFreightRate.destination_port_id == request['destination_port_id'],
    FclFreightRate.destination_main_port_id == request['destination_main_port_id'] if request.get('destination_main_port_id') else (FclFreightRate.id.is_null(False)),
    FclFreightRate.container_size == request['container_size'],
    FclFreightRate.container_type == request['container_type'],
    FclFreightRate.commodity == request['commodity'],
    FclFreightRate.shipping_line_id == request['shipping_line_id'],
    FclFreightRate.importer_exporter_id == request['importer_exporter_id'] if request.get('importer_exporter_id') else (FclFreightRate.importer_exporter_id.is_null(True)),
    FclFreightRate.last_rate_available_date >= date.today()).execute()

    for freight in freight_objects:
        freight.set_platform_prices()
        freight.set_is_best_price()
        freight.save()