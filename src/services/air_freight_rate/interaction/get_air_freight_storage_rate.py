
from libs.json_encoder import json_encoder

def get_air_freight_storage_rate(request):
    
    if not request.get('airport_id') and not request.get('airline_id') and not request.get('trade_type') and not request.get('commodity') and not request.get('service_provider_id'):
        return {}

    detail = AirFreightStorageRate.where(
        AirFreightStorageRate.airport_id == request.get('airport_id'),
        AirFreightStorageRate.airline_id == request.get('airline_id'),
        AirFreightStorageRate.trade_type == request.get('trade_type'),
        AirFreightStorageRate.commodity == request.get('commodity'),
        AirFreightStorageRate.service_provider_id == request.get('service_provider_id')
    ).execute()

    if not detail:
        return {}
    
    return json_encoder(detail)

