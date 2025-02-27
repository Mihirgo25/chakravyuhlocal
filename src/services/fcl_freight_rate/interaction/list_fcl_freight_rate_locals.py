from services.fcl_freight_rate.models.fcl_freight_rate_local import FclFreightRateLocal
import json
from datetime import datetime
from libs.json_encoder import json_encoder
from libs.get_filters import get_filters
from libs.get_applicable_filters import get_applicable_filters
from micro_services.client import *
from libs.apply_eligible_lsp_filters import apply_eligible_lsp_filters
from playhouse.shortcuts import model_to_dict

possible_direct_filters = ['id', 'port_id', 'country_id', 'terminal_id', 'trade_id', 'continent_id', 'shipping_line_id', 'service_provider_id', 'trade_type', 'container_size', 'container_type', 'is_line_items_error_messages_present', 'is_line_items_info_messages_present', 'main_port_id', 'rate_type']
possible_indirect_filters = ['is_detention_missing', 'is_demurrage_missing', 'is_plugin_missing', 'location_ids', 'commodity', 'procured_by_id', 'is_rate_available', 'updated_at_greater_than', 'updated_at_less_than', 'except_shipping_line_id']

def list_fcl_freight_rate_locals(filters = {}, page_limit =10, page=1, sort_by='updated_at', sort_type='desc', return_query=False, get_count = False):
    query = get_query(sort_by, sort_type)

    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)
            
        if filters.get('rate_type') == 'all':
            filters.pop('rate_type')
            
        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)
        query = get_filters(direct_filters, query, FclFreightRateLocal)
        query = apply_indirect_filters(query, indirect_filters)
    if not filters or not 'service_provider_id' in filters:
        query = apply_eligible_lsp_filters(query, FclFreightRateLocal, 'fcl_freight')
    
    if get_count:
        return {'list':query.count()}

    query = query.paginate(page, page_limit)

    if return_query:
        items = [model_to_dict(item) for item in query.execute()]
        return {'list': items}

    data = get_data(query)

    return { 'list': data }


def get_query(sort_by, sort_type):
    query = FclFreightRateLocal.select(
                FclFreightRateLocal.id,
                FclFreightRateLocal.port_id,
                FclFreightRateLocal.main_port_id,
                FclFreightRateLocal.shipping_line_id,
                FclFreightRateLocal.service_provider_id,
                FclFreightRateLocal.trade_type,
                FclFreightRateLocal.container_size,
                FclFreightRateLocal.container_type,
                FclFreightRateLocal.commodity,
                FclFreightRateLocal.selected_suggested_rate_id,
                FclFreightRateLocal.is_line_items_error_messages_present,
                FclFreightRateLocal.line_items_error_messages,
                FclFreightRateLocal.is_line_items_info_messages_present,
                FclFreightRateLocal.line_items_info_messages,
                FclFreightRateLocal.data,
                FclFreightRateLocal.created_at,
                FclFreightRateLocal.updated_at,
                FclFreightRateLocal.procured_by_id,
                FclFreightRateLocal.sourced_by_id,
                FclFreightRateLocal.shipping_line,
                FclFreightRateLocal.port,
                FclFreightRateLocal.main_port,
                FclFreightRateLocal.service_provider,
                FclFreightRateLocal.procured_by,
                FclFreightRateLocal.sourced_by,
                FclFreightRateLocal.rate_type
            ).order_by(eval('FclFreightRateLocal.{}.{}()'.format(sort_by,sort_type)))
    return query

def get_data(query):
    data = []

    all_list = json_encoder(list(query.dicts()))

    for result in all_list:
        result['line_items'] = result['data'].get('line_items')

        result['total_price'] = 0
        if result['line_items']:
            result['total_price_currency'] = result['line_items'][0].get('currency')
        else:
            result['total_price_currency'] = None

        if result['total_price_currency']:
            total_price = 0
            for line_item in result['line_items']:
                if line_item['currency'] != result['total_price_currency']:
                    conversion = common.get_money_exchange_for_fcl({"price":line_item['price'], "from_currency":line_item['currency'], "to_currency":result['total_price_currency']})
                    if 'price' in conversion:
                        total_price += conversion['price']
                else:
                    total_price += int(line_item['price'])
            result['total_price'] = total_price
        result['is_local_agent_rate'] = False
        data.append(result)
    return data

def apply_indirect_filters(query, filters):
    for key in filters:
        if key in possible_indirect_filters:
            apply_filter_function = f'apply_{key}_filter'
            query = eval(f'{apply_filter_function}(query, filters)')
    return query

def apply_is_detention_missing_filter(query, filters):
    is_messages = False
    if filters['is_detention_slabs_missing'] == True or filters['is_detention_slabs_missing'] == 'True':
      is_messages = True
    if is_messages:
      query =  query.where(FclFreightRateLocal.is_detention_slabs_missing)
    else:
        query =  query.where((FclFreightRateLocal.is_detention_slabs_missing == None | ~FclFreightRateLocal.is_detention_slabs_missing))
    return query

def apply_is_demurrage_missing_filter(query, filters):
    is_messages = False
    if filters['is_demurrage_slabs_missing'] == True or filters['is_demurrage_slabs_missing'] == 'True':
      is_messages = True
    if is_messages:
      query =  query.where(FclFreightRateLocal.is_demurrage_slabs_missing)
    else:
        query =  query.where((FclFreightRateLocal.is_demurrage_slabs_missing == None | ~FclFreightRateLocal.is_demurrage_slabs_missing))
    return query

def apply_is_plugin_missing_filter(query, filters):
    is_messages = False
    if filters['is_plugin_slabs_missing'] == True or filters['is_plugin_slabs_missing'] == 'True':
      is_messages = True
    if is_messages:
      query =  query.where(FclFreightRateLocal.is_plugin_slabs_missing)
    else:
        query =  query.where((FclFreightRateLocal.is_plugin_slabs_missing == None | ~FclFreightRateLocal.is_plugin_slabs_missing))

    return query

def apply_is_rate_available_filter(query, filters):
    if filters['is_rate_available'] == False:
        query = query.where(FclFreightRateLocal.rate_not_available_entry)
    else:
        query = query.where((FclFreightRateLocal.rate_not_available_entry == None) | (~FclFreightRateLocal.rate_not_available_entry))
    return query

def apply_location_ids_filter(query, filters):
    location_ids = filters['location_ids']
    query = query.where(FclFreightRateLocal.location_ids.contains_any(location_ids))
    return query

def apply_commodity_filter(query, filters):
    if isinstance(filters['commodity'],str):
        filters['commodity'] = [filters['commodity']]
    if 'general' in filters['commodity']:
        query = query.where((FclFreightRateLocal.commodity == None) | (FclFreightRateLocal.commodity.in_(filters['commodity'])))
    else:
        query = query.where(FclFreightRateLocal.commodity.in_(filters['commodity']))
    return query

def apply_except_shipping_line_id_filter(query, filters):
    shipping_line_ids = filters['except_shipping_line_id']
    if not isinstance(shipping_line_ids, list):
        shipping_line_ids = [shipping_line_ids]
    query=query.where(~FclFreightRateLocal.shipping_line_id << shipping_line_ids)
    return query

def apply_updated_at_greater_than_filter(query, filters):
    query = query.where(FclFreightRateLocal.updated_at.cast('date') >= datetime.fromisoformat(filters['updated_at_greater_than']).date())
    return query

def apply_updated_at_less_than_filter(query, filters):
    query = query.where(FclFreightRateLocal.updated_at <= datetime.fromisoformat(filters['updated_at_less_than']).date())
    return query

def apply_procured_by_id_filter(query, filters):
    query = query.where(FclFreightRateLocal.procured_by_id == filters['procured_by_id'])
    return query
