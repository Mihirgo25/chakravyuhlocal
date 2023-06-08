from services.air_freight_rate.models.air_freight_rate_local import AirFreightRateLocal
from fastapi import HTTPException
from configs.global_constants import PREDICTED_RATES_SERVICE_PROVIDER_IDS
from configs.global_constants import AIR_STANDARD_VOLUMETRIC_WEIGHT_CONVERSION_RATIO
from database.rails_db import get_organization

def get_air_freight_local_rate_cards(request):
    local_query = initialize_local_query(request)
    local_query_results = local_query_results(local_query)
    list = build_response_list(request,local_query_results)
    list = ignore_non_eligible_service_providers(list)


def initialize_local_query(request):    
    params = {
      'airport_id'== request.get('airport_id'),
      'trade_type'== request.get('trade_type'),
      'commodity'== request.get('commodity'),
      'commodity_type'== request.get('commodity_type'),
      'is_line_items_error_messages_present'== False
    }
    if request.airline_id is not None:
        params['airline_id']=request.get('airline_id')

    try:
        objects = AirFreightRateLocal.get(**params)
    except:
        raise HTTPException(status_code=400, detail="no local rate cards entry with the given id exists") 
    return objects

def local_query_results(local_query):
    selected_columns = ['service_provider_id', 'airline_id', 'line_items']
    result = [row for row in local_query.values(*selected_columns)]
    return [dict(row) for row in result]

def build_response_list(request,local_query_results):
    response_list = []
    for result in local_query_results:
        response_object = build_response_object(request,result)

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
       line_item=build_local_line_item_object(request,line_item) 


def build_local_line_item_object(request,line_item):
    chargeable_weight = get_chargeable_weight(request)

def get_chargeable_weight(request):
    volumetric_weight = request.get('volume') * AIR_STANDARD_VOLUMETRIC_WEIGHT_CONVERSION_RATIO
    chargeable_weight=volumetric_weight if volumetric_weight>request.get('weight') else request.get('weight')
    chargeable_weight = round(chargeable_weight, 2)

    return chargeable_weight

def ignore_non_eligible_service_providers(list):
    ids=get_organization(id=list.ids)
