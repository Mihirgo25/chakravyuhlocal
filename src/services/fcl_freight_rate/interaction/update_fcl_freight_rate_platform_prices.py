from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from datetime import date
from peewee import fn


def update_fcl_freight_rate_platform_prices(self,origin_port_id, origin_main_port_id, destination_port_id, destination_main_port_id, container_size, container_type, commodity, shipping_line_id, importer_exporter_id):
    freight_objects = FclFreightRate.select().where(
    (FclFreightRate.origin_port_id == origin_port_id),
    (FclFreightRate.origin_main_port_id == origin_main_port_id if origin_main_port_id is not None else True),
    (FclFreightRate.destination_port_id == destination_port_id),
    (FclFreightRate.destination_main_port_id == destination_main_port_id if destination_main_port_id is not None else True),
    (FclFreightRate.container_size == container_size),
    (FclFreightRate.container_type == container_type),
    (FclFreightRate.commodity == commodity),
    (FclFreightRate.shipping_line_id == shipping_line_id)
    ).where(FclFreightRate.importer_exporter_id.in_([None, importer_exporter_id])
    ).where((FclFreightRate.last_rate_available_date >= date.today())).order_by(fn.Random())

    for freight in freight_objects:
        freight.set_platform_prices()
        freight.set_is_best_price()
        freight.save()
