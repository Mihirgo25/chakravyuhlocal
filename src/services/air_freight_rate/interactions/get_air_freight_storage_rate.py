from services.air_freight_rate.models.air_freight_storage_rate import AirFreightStorageRates

def get_air_freight_storage_rate(request):
    
    if not request.get('airport_id') and not request.get('airline_id') and not request.get('trade_type') and not request.get('commodity') and not request.get('service_provider_id'):
        return {}

    object = AirFreightStorageRates.select().where(
        AirFreightStorageRates.airport_id == request.get('airport_id'),
        AirFreightStorageRates.airline_id == request.get('airline_id'),
        AirFreightStorageRates.trade_type == request.get('trade_type'),
        AirFreightStorageRates.commodity == request.get('commodity'),
        AirFreightStorageRates.service_provider_id == request.get('service_provider_id')
    ).first()

    if object and object.detail():
        return object.detail()
    else:
        return {}