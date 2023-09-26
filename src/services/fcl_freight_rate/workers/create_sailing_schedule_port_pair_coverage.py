from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from micro_services.client import maps


def create_sailing_schedules_port_pair_coverages(request):
    data = {
        "origin_port_id": request.get("origin_port_id"),
        "destination_port_id": request.get("destination_port_id"),
        "shipping_line_id": request.get("shipping_line_id"),
    }
    fcl_freight_query = FclFreightRate.select(FclFreightRate.id).wher(
        FclFreightRate.origin_port_id == data["origin_port_id"],
        FclFreightRate.destination_port_id == data["destination_port_id"],
        FclFreightRate.shipping_line_id == data["shipping_line_id"],
        ~(FclFreightRate.rate_not_available_entry),
    )
    if not fcl_freight_query.exists():
        return maps.create_sailing_schedule_port_pair_coverage(data)