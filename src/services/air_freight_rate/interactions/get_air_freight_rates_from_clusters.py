from services.air_freight_rate.models.air_freight_location_cluster_mapping import AirFreightLocationClusterMapping
from services.air_freight_rate.models.air_freight_rate import AirFreightRate


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
    
    critical_rates = AirFreightRate.select(
            AirFreightRate.id,
            AirFreightRate.airline_id,
            AirFreightRate.origin_airport_id,
            AirFreightRate.destination_airport_id,
            AirFreightRate.origin_country_id,
            AirFreightRate.destination_country_id,
            AirFreightRate.operation_type,
            AirFreightRate.commodity,
            AirFreightRate.commodity_type,
            AirFreightRate.commodity_sub_type,
            AirFreightRate.stacking_type,
            AirFreightRate.shipment_type,
            AirFreightRate.validities,
            AirFreightRate.price_type,
            AirFreightRate.rate_type,
            AirFreightRate.service_provider_id,
            AirFreightRate.cogo_entity_id,
            AirFreightRate.source,
            AirFreightRate.updated_at,
            AirFreightRate.surcharge.alias('freight_surcharge')
        ).where(
            AirFreightRate.origin_airport_id == origin_base_airport_id,
            AirFreightRate.destination_airport_id == destination_base_airport_id,
            AirFreightRate.commodity == request.get('commodity'),
            AirFreightRate.commodity_type == request.get('commodity_type'),
            AirFreightRate.commodity_sub_type == request.get('commodity_subtype'),
            ~(AirFreightRate.rate_not_available_entry),
            AirFreightRate.shipment_type == request.get('packing_type'),
            AirFreightRate.stacking_type == request.get('handling_type'),
            AirFreightRate.rate_type == "market_place",
            AirFreightRate.last_rate_available_date >= request['validity_start'],
            AirFreightRate.source != 'predicted'
        )
    
    




    

