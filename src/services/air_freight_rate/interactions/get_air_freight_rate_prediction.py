from micro_services.client import maps,organization,shipment
from datetime import datetime,timedelta
from services.envision.interaction.get_air_freight_predicted_rate import predict_air_freight_rate
from services.air_freight_rate.constants.air_freight_rate_constants import AIR_STANDARD_VOLUMETRIC_WEIGHT_CONVERSION_RATIO,AIR_EXPORTS_HIGH_DENSITY_RATIO,AIR_EXPORTS_LOW_DENSITY_RATIO,AIR_IMPORTS_LOW_DENSITY_RATIO,AIR_IMPORTS_HIGH_DENSITY_RATIO,DEFAULT_AIRLINE_IDS,SLAB_WISE_CHANGE_FACTOR,DEFAULT_SERVICE_PROVIDER_ID
from celery_worker import air_freight_rate_prediction_feedback_delay
from services.air_freight_rate.interactions.create_air_freight_rate import create_air_freight_rate_data
from database.rails_db import get_eligible_orgs,get_saas_schedules_airport_pair_coverages
from configs.env import DEFAULT_USER_ID
from rms_utils.get_money_exchange_for_fcl_fallback import get_money_exchange_for_fcl_fallback
from libs.get_distance import get_air_distance

def get_air_freight_rate_prediction(request):
    currency = 'USD'
    origin_airport_id = request.get('origin_airport_id')
    destination_airport_id = request.get('destination_airport_id')
    locations = maps.list_locations({ 'filters': { 'id': [origin_airport_id, destination_airport_id] }})['list']
    for location in locations:
        if location.get('id') == origin_airport_id:
            country = location['country_id']
            continent = location['continent_id']
            break

    if continent == '72abc4ba-6368-4501-9a86-8065f5c191f8':
        currency = 'EUR'
    elif country == 'ae37679f-9bfe-488f-b488-250c20da2fb5': 
        currency = 'HKD'
    elif country == '6e18d508-87b9-4e7e-a785-b47edc76b0b7':
        currency == 'SGD'
    elif country == '541d1232-58ce-4d64-83d6-556a42209eb7':
        currency = 'INR'


    weight_slabs = [{ 'unit': 'per_kg', 'currency': currency, 'lower_limit': 0.0, 'upper_limit': 45.0, 'tariff_price': 20 },
                    { 'unit': 'per_kg', 'currency': currency, 'lower_limit': 45.1, 'upper_limit': 100.0, 'tariff_price': 30 },
                    { 'unit': 'per_kg', 'currency': currency, 'lower_limit': 100.1,'upper_limit': 300.0, 'tariff_price': 40 },
                    { 'unit': 'per_kg', 'currency': currency, 'lower_limit': 300.1, 'upper_limit': 500.0, 'tariff_price': 50 },
                    { 'unit': 'per_kg', 'currency': currency, 'lower_limit': 500.1, 'upper_limit': 5000.0, 'tariff_price': 60 }]

    density_category = get_density_category(request.get('weight'), request.get('volume'), request.get('trade_type'))
    params = get_params_for_model(request,locations)
    results = []
    for param in params:
        try:
            result = predict_air_freight_rate(param)
            results.append(result)
        except Exception as e:
            pass
    change_factor = SLAB_WISE_CHANGE_FACTOR
    air_freight_rate_prediction_feedback_delay.apply_async(kwargs={'result':results}, queue = 'low')

    current_datetime = datetime.combine(request.get('cargo_clearance_date'), datetime.min.time())
    validity_start = current_datetime
    next_day_datetime = current_datetime + timedelta(days=3)
    validity_end = next_day_datetime
    service_provider_id_eligible = get_eligible_orgs('air_freight')
    service_provider_id_eligible = None
    if service_provider_id_eligible is None:
        service_provider_id_eligible = DEFAULT_SERVICE_PROVIDER_ID

    cogo_envision_id = DEFAULT_USER_ID

    for result in results:
        predicted_price = result.get('predicted_price')
        if currency != 'USD':
            predicted_price = get_money_exchange_for_fcl_fallback('USD', currency, predicted_price)['price']

        if currency == 'INR' and predicted_price < 100:
            predicted_price = predicted_price + 100

        slab_number = 2
        for weight_slab in weight_slabs:
            if slab_number == 0:
                price = predicted_price
            elif slab_number > 0:
                price = predicted_price/(change_factor**slab_number)
            else:
                price = predicted_price *(change_factor**abs(slab_number))
            weight_slab['tariff_price'] = price
            slab_number = slab_number - 1

        try:
            min_price = round(get_money_exchange_for_fcl_fallback('USD', currency, result['predicted_price'])['price'], 2)
            create_air_freight_rate_data({
                'origin_airport_id' : request['origin_airport_id'],
                'destination_airport_id' : request['destination_airport_id'],
                'commodity' : request.get('commodity'),
                'commodity_type' : request.get('commodity_type'),
                'commodity_sub_type': request.get('commodity_subtype'),
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
                'min_price' : min_price,
                'length': 300,
                'breadth': 300,
                'height': 300,
                'source' : 'predicted',
                'rate_type': 'market_place'
                }
            )
        except:
            raise

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

def get_params_for_model(request, locations):
    params = []
    serviceable_airline_ids = get_saas_schedules_airport_pair_coverages(request.get('origin_airport_id'),request.get('destination_airport_id'))
    top_three_airline_ids = DEFAULT_AIRLINE_IDS
    if serviceable_airline_ids:
        top_three_airline_ids = serviceable_airline_ids[:3]
    
        for loc in locations:
            if loc["id"] == request.get('origin_airport_id'):
                origin_location = (loc["latitude"], loc["longitude"])
            if loc["id"] == request.get('destination_airport_id'):
                destination_location = (loc["latitude"], loc["longitude"])
        try:
            air_route_distance = maps.get_air_route({'origin_airport_id':request['origin_airport_id'], 'destination_airport_id':request['destination_airport_id'], 'includes':['length']})
            if air_route_distance and isinstance(air_route_distance, dict):
                Distance = air_route_distance['length']
            else:
                Distance = get_air_distance(origin_location[0],origin_location[1], destination_location[0], destination_location[1])
        except:
            Distance = 2500
    for id in top_three_airline_ids:
        same_parameter = {
            "origin_airport_id": request["origin_airport_id"],
            "destination_airport_id": request["destination_airport_id"],
            "volume": request["volume"],
            'shipment_type':request['packing_type'],
            'stacking_type':request['handling_type'],
            "airline_id": id,
            "commodity":request['commodity'],
            "air_distance":Distance
        }
        params.append(same_parameter.copy())

    return params