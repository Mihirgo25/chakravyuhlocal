import math
import json
from services.ftl_freight_rate.models.ftl_freight_rate import FtlFreightRate
from services.ftl_freight_rate.interactions.list_trucks import list_trucks_data
from services.ftl_freight_rate.interactions.get_ftl_freight_rate_estimation import get_ftl_freight_rate_estimation
from libs.json_encoder import json_encoder
from database.rails_db import get_eligible_orgs
from micro_services.client import maps,common
from operator import attrgetter
from itertools import groupby
from configs.global_constants import CONFIRMED_INVENTORY
from configs.definitions import FTL_FREIGHT_CHARGES
from services.ftl_freight_rate.models.ftl_freight_rate_audit import FtlFreightRateAudit

# [{
#     id:
#     service_provider_id:
#     origin_location_id:
#     destination_location_id:
#     importer_exporter_id:
#     line_items: [{
#       name:
#       code:
#       unit:
#       quantity:
#       price:
#       total_price:
#       currency:
#       remarks:
#     }]
#     truck_body_type:
#     transit_time:
#     detention_free_time:
#     validity_start:
#     validity_end:
#     truck_type:
#     trucks_count:
#  }]

def get_ftl_freight_rate_cards(request):
    set_callback_for_request(request)
    if request.get('trucks_count') is None and request.get('load_selection_type') == 'trucks':
        return {"list":[]}
    query = select_fields()
    query = initialize_query(query,request)
    rate_list = ignore_non_eligible_service_providers(request,query)
    rate_list = build_response_list(rate_list,request)
    if request.get('include_additional_response_data'):
        rate_list = additional_response_data(rate_list)

    if request.get('predicted_rate'):
        rate_list = remove_unnecessary_fields(rate_list)

    return {'list': rate_list }



def initialize_query(query,request):

    filters = {'commodity': request.get('commodity'),'trip_type': request.get('trip_type'),'rate_not_available_entry': False, 'is_line_items_error_messages_present': False, 'truck_type': request.get('truck_type')}

    for key in filters.keys():
        if filters.get(key) is not None:
            query = query.where(attrgetter(key)(FtlFreightRate) == filters[key])

    query = query.where((FtlFreightRate.importer_exporter_id == request.get("importer_exporter_id")) | (FtlFreightRate.importer_exporter_id.is_null(True)))
    if request.get('load_selection_type') in ['cargo_per_package', 'cargo_gross']:
        query = query.where(FtlFreightRate.unit == 'ton')
    elif request.get('load_selection_type')  == 'truck':
        query = query.where((FtlFreightRate.unit ==  'per_truck') | (FtlFreightRate.unit.is_null(True)))

    origin_location_ids = [request.get('origin_location_id'),request.get('origin_city_id')]
    origin_location_ids = [location_id for location_id in origin_location_ids if location_id is not None]

    if len(origin_location_ids) > 0:
        query = query.where(FtlFreightRate.origin_location_id << origin_location_ids)

    destination_location_ids = [request.get('destination_location_id'),request.get('destination_city')]
    destination_location_ids = [location_id for location_id in destination_location_ids if location_id is not None]

    if len(destination_location_ids) > 0:
        query = query.where(FtlFreightRate.destination_location_id << destination_location_ids)

    if request.get('origin_city_id'):
        query = query.where((FtlFreightRate.origin_location_id == request.get('origin_city_id')) | (FtlFreightRate.origin_city_id == request.get('origin_city_id')))
    if request.get('destination_city_id'):
        query = query.where((FtlFreightRate.destination_location_id == request.get('destination_city_id')) | (FtlFreightRate.destination_city_id == request.get('destination_city_id')))

    if request.get('origin_country_id'):
        query = query.where(FtlFreightRate.origin_country_id == request.get('origin_country_id'))
    if request.get('destination_country_id'):
        query = query.where(FtlFreightRate.destination_country_id == request.get('destination_country_id'))
    cargo_readiness_date = request.get('cargo_readiness_date')
    query = query.where((FtlFreightRate.validity_start <= cargo_readiness_date) &  (FtlFreightRate.validity_end >= cargo_readiness_date))

    return query

def select_fields():
    return FtlFreightRate.select(FtlFreightRate.id, FtlFreightRate.commodity, FtlFreightRate.line_items, FtlFreightRate.service_provider_id, FtlFreightRate.importer_exporter_id, FtlFreightRate.origin_location_id, FtlFreightRate.destination_location_id, FtlFreightRate.origin_destination_location_type, FtlFreightRate.transit_time, FtlFreightRate.detention_free_time, FtlFreightRate.truck_type, FtlFreightRate.minimum_chargeable_weight, FtlFreightRate.unit, FtlFreightRate.validity_start, FtlFreightRate.validity_end,FtlFreightRate.service_provider,FtlFreightRate.sourced_by,FtlFreightRate.updated_at,FtlFreightRate.created_at)

def build_response_list(ftl_rates,request):
    grouping = {}
    for rate in ftl_rates:
        key = ":".join([str(rate["origin_location_id"]) or "", str(rate['destination_location_id']) or "", str(rate["service_provider_id"]) or "" , str(rate['transit_time']) or ""])
        if grouping.get(key) and grouping[key].get('importer_exporter_id'):
            continue
        response_object =  build_response_object(rate,request)
        if response_object:
            grouping[key] = response_object

    return list(grouping.values())



def set_callback_for_request(request):
    if request.get('origin_location_id') and request.get('destination_location_id'):
            location_ids = [request.get('origin_location_id'), request.get('destination_location_id')]
            location_mapping = get_location_mapping(location_ids)
            request['origin_city_id'] = location_mapping.get(request.get('origin_location_id')).get('city_id')
            request['destination_city_id'] = location_mapping.get(request.get('destination_location_id')).get('city_id')
    if request.get('break_point_location_ids') and type(request.get('break_point_location_ids')) != list:
            request['break_point_location_ids'] = json.loads(request.get('break_point_location_ids'))
    if request.get('additional_services') and type(request.get('additional_services')) != list:
            request['additional_services'] = json.loads(request.get('additional_services'))
    request['trip_type'] = 'round_trip' if request.get('trip_type') == 'round' else request.get('trip_type')

def get_location_mapping(location_ids):
    location_data = maps.list_locations({"filters": {"id": location_ids}})["list"]
    location_mapping = {}
    for data in location_data:
        location_mapping[data["id"]] = data
    return location_mapping

def build_response_object(result,request):
    response_object = {
      'id': result.get('id'),
      'origin_location_id': result.get('origin_location_id'),
      'destination_location_id': result.get('destination_location_id'),
      'origin_destination_location_type': result.get('origin_destination_location_type'),
      'service_provider_id': result.get('service_provider_id'),
      'importer_exporter_id': result.get('importer_exporter_id'),
      'line_items': [],
      'source': 'spot_rates' if request.get('predicted_rate')  else  'predicted',
      'tags': [],
      'truck_type': request.get('truck_type'),
      'trucks_count': request.get('trucks_count'),
      'transit_time': result.get('transit_time'),
      'detention_free_time': result.get('detention_free_time'),
      'validity_start': result.get('validity_start'),
      'validity_end': result.get('validity_end'),
      'service_provider': result.get('service_provider'),
      'sourced_by': result.get('sourced_by'),
      'created_at':result.get('created_at'),
      'updated_at':result.get('updated_at')
    }
    if request.get('load_selection_type') in ['cargo_per_package', 'cargo_gross']:
        response_object =  response_object | get_truck_type_and_count(request,result['truck_type'])

    if response_object['service_provider_id'] in CONFIRMED_INVENTORY['service_provider_ids']:
        response_object['tags'] = CONFIRMED_INVENTORY['tag']

    result_line_items = result['line_items'] if type(result['line_items']) == list else list(result['line_items'])
    for line_item in result_line_items:

        if line_item['code'] == 'FSC' and line_item['unit'] == 'percentage_of_freight':
            required_line_items = result['line_items'] if type(result['line_items']) == list else list(result['line_items'])
            for required_line_item in required_line_items:

                if required_line_item['code'] != 'BAS':
                    continue

                line_item_object = build_line_item_object(request,required_line_item, response_object['truck_count'],result['minimum_chargeable_weight'], result['maximum_chargeable_weight']) | {}
                total_price = (float(line_item_object.get('total_price') if line_item_object.get('total_price') else 0 )* float(line_item.get('price') if line_item.get('price') else 0))/ 100
                line_item['total_price'] = total_price
                line_item['price'] = line_item['total_price']
                line_item['quantity'] = 1
                code_config = FTL_FREIGHT_CHARGES[line_item['code']]
                line_item['name'] = code_config['name']
        else:
            line_item = build_line_item_object(request,line_item, response_object['trucks_count'], result['minimum_chargeable_weight'])

        if line_item is None:
            continue
        response_object['line_items'].append(line_item)

    additional_charge_code = []
    for line_item in result_line_items:
        additional_charge_code.append(line_item['code'])

    if request.get('additional_services') is not None:
        for code in request.get('additional_services'):
            if code not in additional_charge_code:
                return False

    return response_object

def build_line_item_object(request,line_item, trucks_count = 0, minimum_chargeable_weight = 0):

    code_config = FTL_FREIGHT_CHARGES[line_item['code']]
    is_additional_service = True if 'additional_services' in list(code_config.get('tags')) else False
    if is_additional_service and line_item['code'] not in request['additional_services']:
        return 0
    line_item_copy = {}
    for key in ['code','unit','price','currency','remarks']:
         line_item_copy[key] = line_item[key]

    line_item = line_item_copy
    alternative_truck_count = get_chargeable_weight(minimum_chargeable_weight) if line_item['unit'] == 'per_ton' else 1
    line_item['quantity'] =  trucks_count if line_item['unit'] == 'per_truck' else  alternative_truck_count
    line_item['total_price'] = line_item['quantity'] * line_item['price']
    line_item['name'] = code_config['name']
    line_item['source'] = 'system'

    return line_item

def get_truck_type_and_count(request, truck_type):
    filters = {"truck_name": truck_type}
    trucks_data = list_trucks_data(filters)['list']
    truck_capacity = trucks_data['capacity']
    truck_count = math.ceil((request.get('weight') / truck_capacity))
    return { 'truck_type': truck_type, 'trucks_count': truck_count }

def get_chargeable_weight(minimum_chargeable_weight,request):
     chargeable_rate = max([request.get('weight'), minimum_chargeable_weight])
     return chargeable_rate

def ignore_non_eligible_service_providers(request,query_result):
    ftl_rates = list(query_result.dicts())
    ids = get_eligible_orgs('ftl_freight')
    final_list = []
    for data in ftl_rates:
        if str(data.get('service_provider_id')) in ids:
            final_list.append(data)
    
    return check_for_prediction(request,final_list)

def check_for_prediction(request,rate_list):
    response = None
    if len(rate_list) == 0 and request.get('predicted_rate') is True and request.get('origin_location_id') is not None and request.get('destination_location_id') is not None:
        rate_estimation_params = {
        'origin_location_id': request.get('origin_location_id'),
        'destination_location_id': request.get('destination_location_id'),
        'trip_type': request.get('trip_type'),
        'truck_type': request.get('truck_type'),
        'commodity': request.get('commodity'),
        'weight': request.get('weight'),
        }
        response = get_ftl_freight_rate_estimation(rate_estimation_params)
    if response is not None:
        request['predicted_rate'] = False
        rate_list = get_ftl_freight_rate_cards(request)['list']
    return rate_list

def additional_response_data(list_of_data):
    for data in list_of_data:

        data['last_updated_at'] = data.get('updated_at')
        data['buy_rate_currency'] = 'INR'
        data['buy_rate'] = get_buy_rate(data['line_items'])

        if data['service_provider'] is not None:
            data['service_provider_name'] = data['service_provider'].get('short_name')
        user = data.get('sourced_by')
        if user is not None:
            data['user_name'] = user.get('name')
            data['user_contact'] = user.get('mobile_number') or user.get('mobile_number_eformat')

    return list_of_data


def get_buy_rate(line_items):
    net_price  = 0
    for line_item_data in line_items:
        price =  common.get_money_exchange_for_fcl({"from_currency": line_item_data["currency"],"to_currency": line_item_data["buy_rate_currency"],"price": line_item_data['price']*line_item_data['quantity']})["price"]
        net_price += int(price)

    return net_price

def remove_unnecessary_fields(data):
    required_fields = ['id', 'origin_location_id', 'destination_location_id', 'origin_destination_location_type', 'service_provider_id', 'importer_exporter_id', 'line_items', 'source', 'tags', 'truck_type', 'trucks_count', 'transit_time', 'detention_free_time','validity_start','validity_end','service_provider_name','user_name','user_contact','last_updated_at','buy_rate_currency','buy_rate']
    final_list = []
    for main_data in data:
        copy_of_main_data = dict()
        for field in required_fields:
            copy_of_main_data[field] = main_data.get(field)
        final_list.append(copy_of_main_data)

    return final_list



