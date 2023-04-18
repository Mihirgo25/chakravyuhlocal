from services.envision.models.fcl_freight_rate_estimation import FclFreightRateEstimation


def get_eligible_estimated_rate(request):
    estimated_rate = FclFreightRateEstimation.select().where(
        FclFreightRateEstimation.origin_location_id <<request['origin_location_ids'],
        FclFreightRateEstimation.destination_location_id << request['destination_location_ids'],
        FclFreightRateEstimation.container_size == request['container_size'],
        FclFreightRateEstimation.container_type == request['container_type']
    )



def get_most_eligible(query,request):
    if query.count()==1:
        return query
    
    port_to_port = query.where(FclFreightRateEstimation.origin_location_id==request.origin_port_id,FclFreightRateEstimation.destination_location_id==request.destination_port_id)
    









