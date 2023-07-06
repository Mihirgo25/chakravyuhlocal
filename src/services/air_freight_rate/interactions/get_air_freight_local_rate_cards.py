from services.air_freight_rate.models.air_freight_rate_local import AirFreightRateLocal
from fastapi import HTTPException
from configs.global_constants import PREDICTED_RATES_SERVICE_PROVIDER_IDS
from services.air_freight_rate.constants.air_freight_rate_constants import AIR_STANDARD_VOLUMETRIC_WEIGHT_CONVERSION_RATIO
from fastapi.encoders import jsonable_encoder
from configs.definitions import AIR_FREIGHT_LOCAL_CHARGES
from micro_services.client import organization
from database.rails_db import get_eligible_orgs

def get_air_freight_local_rate_cards(request):
    local_query = initialize_local_query(request)
    local_query_results = jsonable_encoder(list(local_query.dicts()))
    local_freight_rates = build_response_list(request,local_query_results)
    local_freight_rates = ignore_non_eligible_service_providers(local_freight_rates)

    return {'list':local_freight_rates}


def initialize_local_query(request):    
    query = AirFreightRateLocal.select(AirFreightRateLocal.service_provider_id,AirFreightRateLocal.airline_id,AirFreightRateLocal.line_items).where(
        AirFreightRateLocal.airport_id == request.get('airport_id'),
        AirFreightRateLocal.trade_type == request.get('trade_type'),
        AirFreightRateLocal.commodity == request.get('commodity'),
        AirFreightRateLocal.commodity_type == request.get('commodity_type'),
        AirFreightRateLocal.is_line_items_error_messages_present == False
    )

    if request.get('airline_id'):
        query = query.where(AirFreightRateLocal.airline_id == request.get('airline_id'))
    
    return query

def local_query_results(local_query):
    selected_columns = ['service_provider_id', 'airline_id', 'line_items']
    result = [row for row in local_query.values(*selected_columns)]
    return [dict(row) for row in result]

def build_response_list(request,local_query_results):
    response_list = []
    for result in local_query_results:
        response_object = build_response_object(request,result)
        if response_object:
            response_list.append(response_object)
    
    return response_list

def build_response_object(request,query_result):
    response_object={
        'service_provider_id':query_result.get('service_provider_id'),
        'airline_id':query_result.get('airline_id'),
        'source': 'predicted' if query_result.get('service_provider_id') in PREDICTED_RATES_SERVICE_PROVIDER_IDS else 'spot_rates'
    }
    if not build_local_line_items(request,query_result, response_object):
        return  
    return response_object

def build_local_line_items(request,query_result, response_object):
    response_object['line_items'] = []

    for line_item in query_result['line_items']:
       line_item = build_local_line_item_object(request,line_item)
       if not line_item:
           continue
       response_object['line_items'].append(line_item)
    
    additional_services = request.get('additional_services')
    if additional_services and len(additional_services) - len(list(set([t['code'] for t in response_object['line_items']]))) > 0:
        return False
    
    if response_object['line_items']:
        return True
    return False

def build_local_line_item_object(request,line_item):
    chargeable_weight = get_chargeable_weight(request)
    code_config = AIR_FREIGHT_LOCAL_CHARGES[line_item['code']]
    if not code_config:
        return
    if code_config.get('inco_terms') and request.get('inco_term') and request.get('inco_term') not in code_config.get('inco_terms'):
        return
    
    if code_config.get('tags') and 'weight_slabs_required' in code_config.get('tags'):
        required_slab = None
        for slab in line_item['slabs']:
            if slab['lower_limit'] <= chargeable_weight and slab['upper_limit'] >= chargeable_weight:
                required_slab = slab
                break
        if not required_slab:
            return
        line_item['price'] = required_slab['price']
        line_item['currency'] =  required_slab['currency']

    is_additional_service = False
    if 'additional_service' in code_config.get('tags'):
        is_additional_service = True
    if is_additional_service and line_item['code'] not in request.get('additional_services'):
        return
    
    line_item = {key:value for key,value in line_item.items() if key in ['code','unti','price','currency','min_price','remarks']}
    if line_item.get('unit') == 'per_package':
        line_item['quantity'] = request.get('packages_count')
    elif line_item.get('unit') == 'per_kg':
        line_item['quantity'] = chargeable_weight
    else:
        line_item['quantity'] = 1
    
    line_item['total_price'] = line_item['quantity']*line_item['price']
    if line_item['min_price'] > line_item['total_price']:
        line_item['total_price'] = line_item['min_price']
    line_item['name'] = code_config['name']
    line_item['source'] = 'system'

    return line_item

def get_chargeable_weight(request):
    volumetric_weight = request.get('volume') * AIR_STANDARD_VOLUMETRIC_WEIGHT_CONVERSION_RATIO
    chargeable_weight=volumetric_weight if volumetric_weight>request.get('weight') else request.get('weight')
    chargeable_weight = round(chargeable_weight, 2)

    return chargeable_weight

def ignore_non_eligible_service_providers(locals):
    ids = get_eligible_orgs('air_freight')
    final_locals = []
    for local in locals:
        if local['service_provider_id'] in ids:
            final_locals.append(local)
    return final_locals