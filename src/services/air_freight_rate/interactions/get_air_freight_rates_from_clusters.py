from services.air_freight_rate.models.air_freight_location_cluster_mapping import AirFreightLocationClusterMapping


def get_air_freight_rates_from_clusters(request):
    request={
        'origin_airport_id':'bfc25605-e7e9-46b5-bd23-cc8c2d075ca4',
        'destination_airport_id':'1392cc05-1828-455f-90ec-7fdd12646d67'
    }
    request_locations = [request.get('origin_airport_id'),request.get('destination_airport_id')]
    base_airports = AirFreightLocationClusterMapping.select(AirFreightLocationClusterMapping.cluster_id,AirFreightLocationClusterMapping.location_id).where(
        AirFreightLocationClusterMapping.location_id << request_locations
    )
    origin_base_airport_id = None
    destination_base_airport_id = None
    for base in base_airports:
        if str(base.location_id) == request.get('origin_airport_id'):
            origin_base_airport_id = str(base.cluster_id.base_airport_id)
        else:
            destination_base_airport_id = str(base.cluster_id.base_airport_id)
    
    




    

