from services.fcl_freight_rate.models.fcl_freight_rate_local import FclFreightRateLocal
from services.fcl_freight_rate.helpers.find_or_initialize import apply_direct_filters
from configs.global_constants import INTERNAL_BOOKING
from playhouse.shortcuts import model_to_dict
import concurrent.futures, json
from operator import attrgetter
from math import ceil
from micro_services.client import *
from micro_services.client import common

possible_direct_filters = ['port_id', 'country_id', 'trade_id', 'continent_id', 'shipping_line_id', 'trade_type', 'container_size', 'container_type', 'commodity']
possible_indirect_filters = ['location_ids']

def list_fcl_freight_rate_local_suggestions(service_provider_id, filters = {}, page_limit = 10, page = 1, sort_by = 'updated_at', sort_type = 'desc', pagination_data_required = True):
    if type(filters) != dict:
        filters = json.loads(filters)
    query = get_query(filters, service_provider_id, sort_by, sort_type, page, page_limit)

    query = apply_direct_filters(query, filters, possible_direct_filters, FclFreightRateLocal)
    query = apply_indirect_filters(query, filters)

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(eval(method_name), query, page, page_limit, pagination_data_required) for method_name in ['get_data', 'get_pagination_data']]
        results = {}
        for future in futures:
            result = future.result()
            results.update(result)
        
    data = results['get_data']
    pagination_data = results['get_pagination_data']

    return {'list': data } | (pagination_data)

def get_query(filters, service_provider_id, sort_by, sort_type, page, page_limit):
    query = FclFreightRateLocal.select().where(FclFreightRateLocal.service_provider_id == service_provider_id)
    direct_filters = {key:value for key,value in filters.items() if key in possible_direct_filters}
    for key in direct_filters:
        query = query.select().where(attrgetter(key)(FclFreightRateLocal) == filters[key])
    already_added_rates = [item.selected_suggested_rate_id for item in query.execute()]
 
    query = FclFreightRateLocal.select().where(FclFreightRateLocal.service_provider_id.in_([INTERNAL_BOOKING['service_provider_id']]), FclFreightRateLocal.is_line_items_error_messages_present == False).where(FclFreightRateLocal.id.not_in(already_added_rates)).order_by(eval("FclFreightRateLocal.{}.{}()".format(sort_by, sort_type))).paginate(page, page_limit)
    return query 

def apply_indirect_filters(query, filters):
    for key in filters:
        if key in possible_indirect_filters:
            apply_filter_function = f'apply_{key}_filter'
            query = eval(f'{apply_filter_function}(query, filters)')
    return query

def apply_location_ids_filter(query, filters):
    locations_ids = filters['location_ids']
    return query.where(FclFreightRateLocal.location_ids.in_(','.join(locations_ids)))

def get_pagination_data(query, page, page_limit, pagination_data_required):
    if not pagination_data_required:
        return {'get_pagination_data' : {}}

    params = {
      'page': page,
      'total': ceil(query.count()/page_limit),
      'total_count': query.count(),
      'page_limit': page_limit
    }
    return {'get_pagination_data' : params}


def get_data(query, page, page_limit, pagination_data_required):
    data = []
    
    query = query.select(FclFreightRateLocal.id,FclFreightRateLocal.port_id,FclFreightRateLocal.main_port_id,FclFreightRateLocal.shipping_line_id,FclFreightRateLocal.service_provider_id,FclFreightRateLocal.trade_type,FclFreightRateLocal.container_size,FclFreightRateLocal.container_type,FclFreightRateLocal.commodity,FclFreightRateLocal.data)
    for result in query.execute():
        result['line_items'] = result['data'].get('line_items')
        result['detention'] = result['data'].get('detention')
        result['demurrage'] = result['data'].get('demurrage')
        result['plugin'] = result['data'].get('plugin')
        result['is_detention_missing'] = True if not result['detention']['free_limit'] else False
        result['is_demurrage_missing'] = (not result['demurrage']['free_limit']) if result['trade_type'] == 'import' else None
        result['is_plugin_missing'] = (not result['plugin']['free_limit']) if result['container_type'] == 'refer' else None

        result['total_price'] = 0
        result['total_price_currency'] = result['line_items'][0].get('currency')

        if result['total_price_currency']:
            total_price = 0
            for line_item in result['line_items']:
                conversion = common.get_money_exchange_for_fcl({"price":line_item['price'], "from_currency":line_item['currency'], "to_currency":result['total_price_currency']})
                if 'price' in conversion:
                    total_price += conversion['price']
            result['total_price'] = total_price

        data.append(result)
    return {'get_data':data}

# def add_service_objects(data):
#     if data.count == 0:
#         return data 

#     service_objects = common.get_multiple_service_objects_data_for_fcl({'objects': [
#     {
#         'name': 'operator',
#         'filters': { id: list(set([t['shipping_line_id'] for t in data]))},
#         'fields': ['id', 'business_name', 'short_name', 'logo_url']
#     },
#     {      

#         'name': 'location',
#         'filters': {"id": list(set(item for sublist in [[item["port_id"], item["main_port_id"]] for item in data] for item in sublist))},
#         'fields': ['id', 'name', 'display_name', 'port_code', 'type', 'is_icd']
#     },
#     {
#         'name': 'organization',
#         'filters': { id:list(set(item for sublist in [item["service_provider_id"] for item in data] for item in sublist))},
#         'fields': ['id', 'business_name', 'short_name']
#     }
#     ]})
    
#     for i in range(len(data)):
#         data[i]['shipping_line'] = service_objects['operator'][str(data[i]['shipping_line_id'])] if ('operator' in service_objects) and (str(data[i].get('shipping_line_id')) in service_objects['operator']) else None 
#         data[i]['port'] = service_objects['location'][str(data[i]['port_id'])] if ('location' in service_objects) and (str(data[i].get('port_id')) in service_objects['location']) else None
#         if data[i]['main_port_id']:
#             data[i]['main_port'] = service_objects['location'][str(data[i]['main_port_id'])] if ('location' in service_objects) and (str(data[i].get('main_port_id')) in service_objects['location']) else None
#         else:
#             data[i]['main_port'] = None
#         data[i]['service_provider'] = service_objects['organization'][str(data[i]['service_provider_id'])] if 'organization' in service_objects and str(data[i].get('service_provider_id')) in service_objects['organization'] else None

#     return data