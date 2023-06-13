from services.chakravyuh.models.fcl_freight_rate_estimation import FclFreightRateEstimation

def get_shipping_lines_for_prediction(origin_location_ids, destination_location_ids, container_size, container_type):
    query =  FclFreightRateEstimation.select(
        FclFreightRateEstimation.shipping_line_id
        ).where(
            FclFreightRateEstimation.origin_location << origin_location_ids,
            FclFreightRateEstimation.destination_location_id << destination_location_ids,
            FclFreightRateEstimation.container_size == container_size,
            FclFreightRateEstimation.container_type == container_type
        )
    
    estimations = list(query.dicts())

    shipping_line_ids = []

    for estimation in  estimations:
        sl_id = str(estimation['shipping_line_id'])
        if sl_id:
            shipping_line_ids.append(sl_id)
    
    return shipping_line_ids
