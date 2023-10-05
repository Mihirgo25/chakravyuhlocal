from services.chakravyuh.models.fcl_freight_rate_estimation import FclFreightRateEstimation
from micro_services.client import maps


def get_shipping_lines_for_prediction(origin_location_ids, destination_location_ids, container_size, container_type):

    origin_port_id = origin_location_ids[0]
    destination_port_id = destination_location_ids[0]
    coverage_data = {"origin_port_id": origin_port_id, "destination_port_id": destination_port_id}
    serviceable_shipping_lines = maps.get_sailing_schedule_port_pair_coverages(coverage_data)
    if serviceable_shipping_lines:
        return serviceable_shipping_lines

    query =  FclFreightRateEstimation.select(
        FclFreightRateEstimation.shipping_line_id
        ).where(
            FclFreightRateEstimation.origin_location_id << origin_location_ids,
            FclFreightRateEstimation.destination_location_id << destination_location_ids,
            FclFreightRateEstimation.container_size == container_size,
            FclFreightRateEstimation.container_type == container_type
        ).limit(10)
    
    estimations = list(query.dicts())

    shipping_line_ids = []

    for estimation in  estimations:
        sl_id = estimation['shipping_line_id']
        if sl_id:
            shipping_line_ids.append(str(sl_id))
    
    return shipping_line_ids
