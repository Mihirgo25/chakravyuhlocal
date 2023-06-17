from services.air_freight_rate.models.draft_air_freight_rate import DraftAirFreightRate

def create_draft_air_freight_rate(request):
    meta_data = request.get('meta_data') or {}
    meta_data = meta_data | {
        'density_category': request.get('density_category'),
        'shipment_type': request.get('shipment_type'),
        'commodity_sub_type': request.get('commodity_sub_type'),
    }
    payload = {
        'rate_id': request.get('rate_id'),
        'origin_airport_id': request['origin_airport_id'],
        'destination_airport_id': request['destination_airport_id'],
        'weight_slabs': request['weight_slabs'],
        'min_price': request.get('min_price'),
        'commodity': request['commodity'],
        'commodity_type': request.get('commodity_type'),
        'operation_type': request.get('operation_type'),
        'currency': request.get('currency'),
        'price_type': request.get('price_type'),
        'rate_type': request.get('rate_type'),
        'service_provider_id': request.get('service_provider_id'),
        'stacking_type': request.get('stacking_type'),
        'validity_start': request.get('validity_start').date(),
        'validity_end': request.get('validity_end').date(),
        'source': request.get('source'),
        'airline_id': request.get('airline_id'),
        'meta_data': meta_data
    }
    draft = DraftAirFreightRate.create(**payload)

    return draft.id