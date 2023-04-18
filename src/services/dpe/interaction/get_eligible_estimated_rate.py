from services.dpe.models.fcl_freight_rate_estimation import FclFreightRateEstimation


def get_eligible_estimated_rate(request):
    origin_location_ids = [request.get('origin_port_id'),request.get('origin_country_id'),request.get('origin_trade_id')]
    destination_location_ids = [request.get('destination_port_id'),request.get('destination_country_id'),request.get('destination_trade_id')]

    estimated_rate = FclFreightRateEstimation.select(FclFreightRateEstimation.lower_rate,FclFreightRateEstimation.upper_rate).where(
        FclFreightRateEstimation.origin_location_id << origin_location_ids,
        FclFreightRateEstimation.destination_location_id << destination_location_ids,
        FclFreightRateEstimation.container_size == request['container_size'],
        FclFreightRateEstimation.container_type == request['container_type']
    ).order_by(FclFreightRateEstimation.lower_rate.desc())

    estimated_rate ,count = get_most_eligible(estimated_rate,request)

    if count >1:
        estimated_rate = estimated_rate.where(FclFreightRateEstimation.shipping_line_id==request.get('shipping_line_id'))
    
    
    if estimated_rate.count()>1:
        estimated_rate = estimated_rate.where(FclFreightRateEstimation.commodity==request.get('commodity'))

    return estimated_rate.dicts().get()


def get_most_eligible(query,request):
    
    port_to_port = query.where(FclFreightRateEstimation.origin_location_id==request.get("origin_port_id"),FclFreightRateEstimation.destination_location_id==request.get("destination_port_id"))

    count = port_to_port.count()
    if count>0:
        return port_to_port,count
    
    port_to_country = query.where(((FclFreightRateEstimation.origin_location_id==request.get("origin_port_id")) & (FclFreightRateEstimation.destination_location_id==request.get("destination_country_id")))| (
    (FclFreightRateEstimation.origin_location_id==request.get("origin_country_id")) & (FclFreightRateEstimation.destination_location_id==request.get("destination_port_id"))
    ))

    count = port_to_country.count()
    if count>0:
        return port_to_country,count
    

    country_to_country = query.where(FclFreightRateEstimation.origin_location_id==request.get("origin_country_id"),FclFreightRateEstimation.destination_location_id==request.get("destination_country_id"))

    count = country_to_country.count()

    if count>0:
        return country_to_country,count
    
    return query,0
    

    









