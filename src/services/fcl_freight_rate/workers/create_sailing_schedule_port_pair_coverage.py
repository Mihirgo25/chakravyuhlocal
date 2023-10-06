from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from micro_services.client import common



def create_sailing_schedules_port_pair_coverages(request):

    origin_port = request.origin_port
    destination_port = request.destination_port

    origin_port_type = 'icd_port' if origin_port.get('is_icd') else 'main_port'
    destination_port_type = 'icd_port' if destination_port.get('is_icd') else 'main_port'
    port_pair_type = f'{origin_port_type}:{destination_port_type}'

    data = {
        "origin_port_id": str(request.origin_port_id),
        "destination_port_id": str(request.destination_port_id),
        "shipping_line_id": str(request.shipping_line_id),
        "port_pair_type": str(port_pair_type)
    }

    # fcl_freight_query = FclFreightRate.select(FclFreightRate.id).where(
    #                     FclFreightRate.origin_port_id == data["origin_port_id"],
    #                     FclFreightRate.destination_port_id == data["destination_port_id"],
    #                     FclFreightRate.shipping_line_id == data["shipping_line_id"],
    #                     FclFreightRate.rate_not_available_entry == False)

    # if not fcl_freight_query.exists():
    return common.create_sailing_schedule_port_pair_coverage(data)