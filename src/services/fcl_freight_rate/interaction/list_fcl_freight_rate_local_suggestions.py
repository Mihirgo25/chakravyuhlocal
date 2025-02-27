from services.fcl_freight_rate.models.fcl_freight_rate_local import FclFreightRateLocal
from configs.global_constants import INTERNAL_BOOKING
from libs.get_filters import get_filters
from libs.get_applicable_filters import get_applicable_filters
from operator import attrgetter
from math import ceil
from micro_services.client import *
from micro_services.client import common

possible_direct_filters = ['port_id', 'country_id', 'trade_id', 'continent_id', 'shipping_line_id', 'trade_type', 'container_size', 'container_type', 'commodity', 'rate_type']
possible_indirect_filters = ['location_ids']

def list_fcl_freight_rate_local_suggestions(service_provider_id, filters = {}, page_limit = 10, page = 1, sort_by = 'updated_at', sort_type = 'desc', pagination_data_required = True):
    query = get_query(filters, service_provider_id, sort_by, sort_type)
    if filters:
        if filters.get('rate_type') == 'all':
            filters.pop('rate_type')
            
        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)
  
        query = get_filters(direct_filters, query, FclFreightRateLocal)
        query = apply_indirect_filters(query, indirect_filters)

    pagination_data = get_pagination_data(query, page, page_limit, pagination_data_required)
    query = query.paginate(page, page_limit)
    data = get_data(query)

    return {'list': data } | (pagination_data)

def get_query(filters, service_provider_id, sort_by, sort_type):
    query = FclFreightRateLocal.select(FclFreightRateLocal.selected_suggested_rate_id).where(FclFreightRateLocal.service_provider_id == service_provider_id)
    if filters:
        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)
        for key in direct_filters:
            if key == 'commodity':
                if 'general' in filters[key]:
                    query = query.where((attrgetter(key)(FclFreightRateLocal) == None) | (attrgetter(key)(FclFreightRateLocal).in_(filters[key])))
                else:
                    query = query.where(attrgetter(key)(FclFreightRateLocal).in_(filters[key]))
            else:
                query = query.where(attrgetter(key)(FclFreightRateLocal) == filters[key])

    already_added_rates = [item.selected_suggested_rate_id for item in query.execute() if item.selected_suggested_rate_id]
    query = FclFreightRateLocal.select().where(FclFreightRateLocal.service_provider_id.in_([INTERNAL_BOOKING['service_provider_id']]), FclFreightRateLocal.is_line_items_error_messages_present == False)

    if already_added_rates:
        query = query.where(FclFreightRateLocal.id.not_in(already_added_rates))
    query = query.order_by(eval("FclFreightRateLocal.{}.{}()".format(sort_by, sort_type)))
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

def get_pagination_data(query, page, page_limit, pagination_data_required):
    if not pagination_data_required:
        return {}

    total_count = query.count()
    params = {
      'page': page,
      'total': ceil(total_count/page_limit),
      'total_count': total_count,
      'page_limit': page_limit
    }
    return params


def get_data(query):
    data = []
    
    query = query.select(FclFreightRateLocal.id,FclFreightRateLocal.port_id,FclFreightRateLocal.main_port_id,FclFreightRateLocal.shipping_line_id,FclFreightRateLocal.service_provider_id,FclFreightRateLocal.trade_type,FclFreightRateLocal.container_size,FclFreightRateLocal.container_type,FclFreightRateLocal.commodity,FclFreightRateLocal.data,FclFreightRateLocal.rate_type)
    response = query.dicts()
    for result in response:
        result['line_items'] = result['data'].get('line_items')
        result['detention'] = result['data'].get('detention')
        result['demurrage'] = result['data'].get('demurrage')
        result['plugin'] = result['data'].get('plugin')
        result['is_detention_missing'] = True if not result['detention'] or not (result['detention'] or {}).get('free_limit') else False
        result['is_demurrage_missing'] = (not (result['demurrage'] or {}).get('free_limit')) if result['trade_type'] == 'import' else None
        result['is_plugin_missing'] = (not (result['plugin'] or {}).get('free_limit')) if result['container_type'] == 'refer' else None

        result['total_price'] = 0
        result['total_price_currency'] = result['line_items'][0].get('currency')

        if result['total_price_currency']:
            total_price = 0
            for line_item in result['line_items']:
                if line_item['currency']!=result['total_price_currency']:
                    conversion = common.get_money_exchange_for_fcl({"price":line_item['price'], "from_currency":line_item['currency'], "to_currency":result['total_price_currency']})
                    if 'price' in conversion:
                        total_price += conversion['price']
                else:
                    total_price+=line_item['price']
            result['total_price'] = total_price

        data.append(result)
    return data

