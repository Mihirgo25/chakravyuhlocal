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
    query = get_query(filters, service_provider_id, sort_by, sort_type, page, page_limit)
    if filters:
        query = apply_direct_filters(query, filters, possible_direct_filters, FclFreightRateLocal)
        query = apply_indirect_filters(query, filters)
    data = get_data(query)
    pagination_data = get_pagination_data(query, page, page_limit, pagination_data_required)

    return {'list': data } | (pagination_data)

def get_query(filters, service_provider_id, sort_by, sort_type, page, page_limit):
    query = FclFreightRateLocal.select().where(FclFreightRateLocal.service_provider_id == service_provider_id)
    if filters:
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
    return query.where(FclFreightRateLocal.location_ids.contains(locations_ids))

def get_pagination_data(data, page, page_limit, pagination_data_required):
    if not pagination_data_required:
        return {}

    params = {
      'page': page,
      'total': ceil(len(data)/page_limit),
      'total_count': len(data),
      'page_limit': page_limit
    }
    return params


def get_data(query):
    data = []
    
    query = query.select(FclFreightRateLocal.id,FclFreightRateLocal.port_id,FclFreightRateLocal.main_port_id,FclFreightRateLocal.shipping_line_id,FclFreightRateLocal.service_provider_id,FclFreightRateLocal.trade_type,FclFreightRateLocal.container_size,FclFreightRateLocal.container_type,FclFreightRateLocal.commodity,FclFreightRateLocal.data)
    for result in query.dicts():
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
    return data

