from micro_services.client import maps,organization,shipment
from datetime import datetime,timedelta
from services.envision.interaction.get_air_freight_predicted_rate import predict_air_freight_rate
from configs.air_freight_rate_constants import AIR_STANDARD_VOLUMETRIC_WEIGHT_CONVERSION_RATIO,AIR_EXPORTS_HIGH_DENSITY_RATIO,AIR_EXPORTS_LOW_DENSITY_RATIO,AIR_IMPORTS_LOW_DENSITY_RATIO,AIR_IMPORTS_HIGH_DENSITY_RATIO,DEFAULT_AIRLINE_IDS,COGOLENS_URL,SLAB_WISE_CHANGE_FACTOR,DEFAULT_SERVICE_PROVIDER_ID,COGO_ENVISION_ID
from celery_worker import air_freight_rate_envision_feedback_delay
from services.air_freight_rate.interactions.create_air_freight_rate import create_air_freight_rate_data
def get_air_freight_rate_prediction(request):
    currency = 'INR'
    weight_slabs = [{ 'unit': 'per_kg', 'currency': currency, 'lower_limit': 0.0, 'upper_limit': 45.0, 'tariff_price': 20 },
                    { 'unit': 'per_kg', 'currency': currency, 'lower_limit': 45.1, 'upper_limit': 100.0, 'tariff_price': 30 },
                    { 'unit': 'per_kg', 'currency': currency, 'lower_limit': 100.1,'upper_limit': 300.0, 'tariff_price': 40 },
                    { 'unit': 'per_kg', 'currency': currency, 'lower_limit': 300.1, 'upper_limit': 500.0, 'tariff_price': 50 },
                    { 'unit': 'per_kg', 'currency': currency, 'lower_limit': 500.1, 'upper_limit': 5000.0, 'tariff_price': 60 }]
    
    
    density_category = get_density_category(request.get('weight'), request.get('volume'), request.get('trade_type'))
    params = get_params_for_model(currency,request)
    results = []
    for param in params:
        try:
            param['date'] = datetime.now()
            result = predict_air_freight_rate(param)
            results.append(result)
        except Exception as e:
            pass
    change_factor = SLAB_WISE_CHANGE_FACTOR
    for result in results:
        air_freight_rate_envision_feedback_delay.apply_async(kwargs={'result':results}, queue = 'low')
        
    input_for_eligible_service = {
            'service': 'air_freight',
            'data': {
                'origin_airport_id': request.get('origin_airport_id'),
                'destination_airport_id': request.get('destination_airport_id')
            }
        }
        
    current_datetime = datetime.combine(request.get('cargo_clearance_date'), datetime.min.time())
    validity_start = current_datetime
    next_day_datetime = current_datetime + timedelta(days=3)
    validity_end = next_day_datetime
    # need to expose
    service_provider_id_eligible = organization.get_eligible_service_organizations(input_for_eligible_service)
    service_provider_id_eligible = None
    if service_provider_id_eligible is None:
        service_provider_id_eligible = DEFAULT_SERVICE_PROVIDER_ID
    
    cogo_envision_id = COGO_ENVISION_ID
            
    for result in results:
        price = result.get('predicted_price')
    
        for weight_slab in weight_slabs:
            weight_slab['tariff_price'] = price
            price *= change_factor
        try:
            create_air_freight_rate_data({
                'origin_airport_id' : request['origin_airport_id'],
                'destination_airport_id' : request['destination_airport_id'],
                'commodity' : request.get('commodity'),
                'commodity_type' : request.get('commodity_type'),
                'airline_id' : result['airline_id'],
                'operation_type' : 'passenger',
                'density_category' : density_category,
                'currency' : currency,
                'price_type' :'all_in',
                'service_provider_id' :service_provider_id_eligible,
                'performed_by_id' : cogo_envision_id,
                'procured_by_id' : cogo_envision_id,
                'sourced_by_id' : cogo_envision_id,
                'shipment_type': request.get('packing_type'),
                'stacking_type'  : request.get('handling_type'),
                'validity_start' : validity_start,
                'validity_end' : validity_end,
                'weight_slabs' : weight_slabs,
                'min_price' : result['predicted_price'],
                'length': 300,
                'breadth': 300,
                'height': 300,
                'mode' : 'predicted'}
            )
        except Exception as e:
            pass

    return True
        
        
        
    
    

def get_density_category(gross_weight,gross_volume,trade_type):
    ratio = round((gross_volume * AIR_STANDARD_VOLUMETRIC_WEIGHT_CONVERSION_RATIO / float(gross_weight)),4)
    chargeable_weight = get_chargeable_weight(gross_weight,gross_volume)
    if trade_type == 'import':
        low_density_lower_limit = AIR_IMPORTS_LOW_DENSITY_RATIO
        high_density_upper_limit = AIR_IMPORTS_HIGH_DENSITY_RATIO
    else:
        low_density_lower_limit = AIR_EXPORTS_LOW_DENSITY_RATIO
        high_density_upper_limit = AIR_EXPORTS_HIGH_DENSITY_RATIO
    
    if ratio > low_density_lower_limit:
        density_rate_category = 'low_density'
    elif ratio <= high_density_upper_limit and chargeable_weight >= 100:
        density_rate_category = 'high_density'
    else:
        density_rate_category = 'general'
    return density_rate_category

def get_chargeable_weight(weight,volume):
    volumetric_weight = float(volume) * AIR_STANDARD_VOLUMETRIC_WEIGHT_CONVERSION_RATIO
    chargeable_weight = volumetric_weight if volumetric_weight > weight else weight
    return round(chargeable_weight,2)

def get_params_for_model(currency,request):
    default_airlines_ids = DEFAULT_AIRLINE_IDS
    params = []
    no_of_airlines = 3
    data = {}
    data['origin_airport_id'] = request.get('origin_airport_id')
    data['destination_Airport_id'] = request.get('destination_airport_id')
    data['no_of_airlines'] = no_of_airlines
    # top_three_airline_ids = shipment.get_previous_shipment_airlines(data)
    top_three_airline_ids = []
    if len(top_three_airline_ids) < no_of_airlines:
        for airline_id in default_airlines_ids:
            if len(top_three_airline_ids) >= no_of_airlines:
                break
            if airline_id in top_three_airline_ids:
                continue
            top_three_airline_ids.append(airline_id)
    
    for id in top_three_airline_ids:
        same_parameter = {
            "origin_airport_id": request["origin_airport_id"],
            "destination_airport_id": request["destination_airport_id"],
            "weight": request["weight"],
            "volume": request["volume"],
            "packages_count": request["packages_count"],
            "airline_id": id,
            "currency": currency
        }
        params.append(same_parameter.copy())

    return params
    
    