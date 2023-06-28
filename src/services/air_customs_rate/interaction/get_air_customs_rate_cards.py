import  sentry_sdk, traceback
from services.air_customs_rate.models.air_customs_rate import AirCustomsRate
from fastapi.encoders import jsonable_encoder
from database.rails_db import  get_eligible_orgs
from configs.global_constants import PREDICTED_RATES_SERVICE_PROVIDER_IDS,AIR_STANDARD_VOLUMETRIC_WEIGHT_CONVERSION_RATIO
from configs.definitions import AIR_CUSTOMS_CHARGES
from micro_services.client import common
def get_air_customs_rate_cards(request):
    try:
        query = initialize_air_customs_rate_query(request)
        air_customs_rates = jsonable_encoder(list(query.dicts()))

        if len(air_customs_rates) > 0:
            customs_rates = discard_noneligible_lsps(air_customs_rates)
            rate_cards = build_response_list(customs_rates,request)

            return {'list':rate_cards}

        return {'list':[]} 
       
    except Exception as e:
        traceback.print_exc()
        sentry_sdk.capture_exception(e)
        print(e, 'Error In Fcl Customs Rate Cards')
        return {
            "list": []
        }




def initialize_air_customs_rate_query(request):
    query = AirCustomsRate.select(
        AirCustomsRate.line_items,
        AirCustomsRate.service_provider_id,
        AirCustomsRate.importer_exporter_id,
    ).where(
        AirCustomsRate.airport_id == request.get('airport_id'),
        AirCustomsRate.trade_type == request.get('trade_type'),
        AirCustomsRate.rate_not_available_entry == False,
        AirCustomsRate.is_line_items_error_messages_present== False,
        ((AirCustomsRate.importer_exporter_id == request.get('importer_exporter_id')) | (AirCustomsRate.importer_exporter_id==None))
    )
    return query

def discard_noneligible_lsps(air_customs_rates):
    ids = get_eligible_orgs('air_customs')

    air_customs_rates = [rate for rate in air_customs_rates if rate["service_provider_id"] in ids]
    return air_customs_rates

def build_response_list(query_results,request):
    response_list  = []
    grouped_query_results = group_by(query_results)
    for key, rates in grouped_query_results.items():
        result = [rate for rate in rates if rate.get('importer_exporter_id')]
        if result:
            result = result[0]
        else:
            result = rates[0]
        response_object = build_response_object(result, request)
        if response_object:
            response_list .append(response_object) 
        return response_list 

def build_response_object(result,request):
    response_object = {
        'service_provider_id':result.get('service_provider_id'),
        'importer_exporter_id':result.get('importer_exporter_id'),
        'line_items':[],
        'total_price':0,
        'source': 'predicted' if  result.get('service_provider_id') in PREDICTED_RATES_SERVICE_PROVIDER_IDS else 'spot_rates'
    }
    if not add_customs_clearance(result, response_object,request):
        return None

    return response_object

def add_customs_clearance(result,response_object,request):
    total_price = 0
    total_price_currency = result['line_items'][0]['currency']
    if not result.get('line_items'):
        return False

    for line_item in result.get('line_items'):
        line_item = build_line_item_object(line_item,request)
        total_price += common.get_money_exchange_for_fcl({"price": line_item.get('total_price'), "from_currency": line_item.get('currency'), "to_currency": total_price_currency})['price']

        if line_item is None:
            continue

        response_object['line_items'].append(line_item)
    response_object['total_price'] = total_price

    additional_services_count = len(request.get('additional_services')) - len([t['code'] for t in response_object['line_items']])
    if additional_services_count > 0:
        return False

    return bool(response_object['line_items'])
def build_line_item_object(line_item,request):
    custom_code_config = AIR_CUSTOMS_CHARGES.get(line_item.get('code'),'')
    is_additional_service = True if 'additional_service' in custom_code_config.get('tags',[]) else False
    if is_additional_service and line_item.get('code') not in request.get('additional_services') and request.get('additional_services'):
        return
    line_item['quantity'] = request.packages_count if line_item['unit'] == 'per_package' else (get_chargeable_weight() if line_item['unit'] == 'per_kg' else 1)
    line_item['total_price'] = line_item['quantity'] * line_item['price']
    line_item['name'] = custom_code_config.get('name', '')
    line_item['source'] = 'system'

    return line_item

def get_chargeable_weight(request):
    volumetric_weight = request.volume *AIR_STANDARD_VOLUMETRIC_WEIGHT_CONVERSION_RATIO
    chargeable_weight = max(volumetric_weight, request.weight)
    return round(chargeable_weight, 2)

def group_by(query):
    grouped_query_results = {}
    for result in query:
        service_provider_id = result['service_provider_id']
        if service_provider_id not in grouped_query_results:
            grouped_query_results[service_provider_id] = []
        grouped_query_results[service_provider_id].append(result)
    return grouped_query_results


