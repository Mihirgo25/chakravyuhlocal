from services.chakravyuh.models.fcl_freight_rate_estimation import FclFreightRateEstimation
from micro_services.client import maps


def get_serviceable_shipping_lines(request):
    data = {'origin_port_id': request['origin_port_id'],'destination_port_id': request['destination_port_id']}
    resp = maps.get_sailing_schedule_port_pair_serviceability(data)
    return resp

def get_shipping_lines_for_prediction(origin_location_ids, destination_location_ids, container_size, container_type):

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
