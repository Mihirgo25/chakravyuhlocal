from services.fcl_customs_rate.models.fcl_customs_rate import FclCustomsRate
from configs.global_constants import CONFIRMED_INVENTORY
from configs.fcl_customs_rate_constants import LOCATION_HIERARCHY
from configs.definitions import FCL_CUSTOMS_CHARGES
from fastapi.encoders import jsonable_encoder
from database.rails_db import get_eligible_orgs
import sentry_sdk, traceback
from services.fcl_customs_rate.interaction.get_zone_average_customs_rate import get_zone_average_customs_rate

def get_fcl_customs_rate_cards(request):
    try:
        query = initialize_customs_query(request)
        customs_rates = jsonable_encoder(list(query.dicts()))

        if len(customs_rates) == 0 and request.get('port_id'):
            customs_rates = get_zone_average_customs_rate(request)

        customs_rates = discard_noneligible_lsps(customs_rates)
        rate_cards = build_response_list(request, customs_rates)

        return {'list':rate_cards}

    except Exception as e:
        traceback.print_exc()
        sentry_sdk.capture_exception(e)
        print(e, 'Error In Fcl Customs Rate Cards')
        return {
            "list": []
        }

def initialize_customs_query(request):
    location_ids = list(filter(None, [request.get('port_id'), request.get('country_id')]))
    query = FclCustomsRate.select(
        FclCustomsRate.customs_line_items,
        FclCustomsRate.service_provider_id,
        FclCustomsRate.importer_exporter_id,
        FclCustomsRate.location_type,
        FclCustomsRate.location_id,
        FclCustomsRate.mode,
        FclCustomsRate.rate_type
    ).where(
      FclCustomsRate.container_size == request.get('container_size'),
      FclCustomsRate.container_type == request.get('container_type'),
      FclCustomsRate.commodity == request.get('commodity'),
      FclCustomsRate.trade_type == request.get('trade_type'),
      FclCustomsRate.is_customs_line_items_error_messages_present == False,
      FclCustomsRate.rate_not_available_entry == False,
      FclCustomsRate.location_id << location_ids,
      ((FclCustomsRate.importer_exporter_id == request.get('importer_exporter_id')) | (FclCustomsRate.importer_exporter_id.is_null(True))),
      ((FclCustomsRate.cargo_handling_type == request.get('cargo_handling_type')) | (FclCustomsRate.cargo_handling_type.is_null(True)))
    )

    if request.get('country_id'):
        query = query.where(FclCustomsRate.country_id == request.get('country_id'))

    return query


def discard_noneligible_lsps(custom_rates):
    ids = get_eligible_orgs('fcl_customs')
    custom_rates = [rate for rate in custom_rates if rate.get("service_provider_id") in ids]

    return custom_rates

def build_response_list(request, customs_rates):
    list = []
    
    grouped_customs_rates = group_by_key(customs_rates, request)

    for key, rate in grouped_customs_rates.items():
      rates = sorted(rate, key = lambda x: LOCATION_HIERARCHY[x['location_type']] )

      result = [rate for rate in rates if rate.get('importer_exporter_id')]
      if result:
         result = result[0]
      else:
        result = rates[0]

      response_object = build_response_object(result, request)
      if response_object:
        list.append(response_object) 
    return list


def build_response_object(result, request):
    source = 'spot_rates'
    if result.get('mode') == 'predicted':
        source = 'predicted'
    elif result.get('rate_type') != 'market_place':
        source = result.get('rate_type')

    response_object = {
      'service_provider_id': result.get('service_provider_id'),
      'importer_exporter_id': result.get('importer_exporter_id'),
      'location_id': result.get('location_id'),
      'line_items': [],
      'source': source,
      'tags': []
    }

    if response_object['service_provider_id'] in CONFIRMED_INVENTORY['service_provider_ids']:
        response_object['tags'].append(CONFIRMED_INVENTORY['tag']) 

    if not add_customs_clearance(result, response_object, request):
        return  
    return response_object

def add_customs_clearance(result, response_object, request):
    if not result.get('customs_line_items'):
        return False
    
    for line_item in result.get('customs_line_items'):
      custom_line_item = build_line_item_object(line_item, request)

      if custom_line_item:
        response_object['line_items'].append(custom_line_item)

    return True

def build_line_item_object(line_item, request):
    custom_code_config = FCL_CUSTOMS_CHARGES.get(line_item.get('code'),'')
    is_additional_service = True if 'additional_service' in custom_code_config.get('tags',[]) else False

    if is_additional_service and line_item.get('code') not in request.get('additional_services'):
        return 

    line_item = {
        "code": line_item["code"],
        "unit": line_item["unit"],
        "price": line_item["price"],
        "currency": line_item["currency"],
        "remarks": line_item.get("remarks") or []
    }

    line_item['quantity'] = request.get('containers_count') if line_item['unit'] == 'per_container' else 1
    line_item['total_price'] = line_item['quantity'] * line_item['price']
    line_item['name'] = custom_code_config.get('name')
    line_item['source'] = 'system'

    return line_item


def group_by_key(customs_rates, request):
    result = {}
    for item in customs_rates:
        if request.get('port_id'):
            key = f'{str(item["service_provider_id"] or "")}:{str(item["rate_type"])}'
        else:
            key = f'{str(item["service_provider_id"] or "")}:{str(item["location_id"] or "")}:{str(item["rate_type"])}'
        try: 
            result[key].append(item)
        except KeyError:
            result[key] = [item]
    return result