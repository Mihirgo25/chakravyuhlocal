from libs.get_filters import get_filters
from libs.get_applicable_filters import get_applicable_filters
from peewee import *
import json
from services.fcl_cfs_rate.models.fcl_cfs_rate import FclCfsRate
from micro_services.client import common

possible_direct_filters = ['id', 'location_id', 'country_code', 'trade_id', 'content_id', 'trade_type', 'service_provider id', 'importer_exporter_id', 'commodity', 'container_type', 'container_size', 'cargo_handling_type']
possible_indirect_filters = ['location_ids', 'importer_exporter_present', 'is_rate_available']

def list_fcl_cfs_rate(filters = {}, page_limit = 10, page = 1, sort_by = 'updated_at', sort_type = 'desc', return_query = False):
    query = get_query(sort_by, sort_type, page, page_limit)
    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)
        
        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)
  
        query = get_filters(direct_filters, query, FclCfsRate)
        query = apply_indirect_filters(query, indirect_filters)

    if return_query:
        return {'list': query}
    
    data = get_data(query)
    return {'list': data}

def get_query(sort_by, sort_type, page, page_limit):
    query = FclCfsRate.select().order_by(eval(f"FclCfsRate.{sort_by}.{sort_type}()")).paginate(page, page_limit)
    return query

def apply_indirect_filters(query, filters):
  for key in filters:
    apply_filter_function = f'apply_{key}_filter'
    query = eval(f'{apply_filter_function}(query, filters)')
  return query

def apply_location_ids_filter(query, location_ids):
    query = query.where(FclCfsRate.location_ids << location_ids)
    return query

def apply_is_rate_available_filter(query, filters):
    rate_not_available_entry = not filters.get('is_rate_available')
    query = query.where(FclCfsRate.rate_not_available_entry == rate_not_available_entry)
    return query

def get_data(query):
    query_result = query.select(
        FclCfsRate.id,
        FclCfsRate.location_id,
        FclCfsRate.service_provider_id,
        FclCfsRate.trade_type,
        FclCfsRate.importer_exporter_id,
        FclCfsRate.commodity,
        FclCfsRate.container_type,
        FclCfsRate.container_size,
        FclCfsRate.cfs_line_items,
        FclCfsRate.is_cfs_line_items_error_messages_present,
        FclCfsRate.is_cfs_line_items_info_messages_present,
        FclCfsRate.cfs_line_items_error_messages,
        FclCfsRate.cfs_line_items_info_messages,
        FclCfsRate.cargo_handling_type).dicts()

    data = list(query_result)
    for object in data:
        object['total_price_currency'] = 'INR'
        object['total_price'] = get_total_price(object['line_items'], object['total_price_currency'])

    return data
        
def apply_importer_exporter_present_filter(query, filters):
    if filters['importer_exporter_present']:
        return query.where(FclCfsRate.importer_exporter_id != None)
  
    query = query.where(FclCfsRate.importer_exporter_id == None)
    return query

def get_total_price(line_items, total_price_currency):
    total_price = 0
    for line_item in line_items:
        total_price += common.get_money_exchange_for_fcl({"price": line_item.get('price'), "from_currency": line_item.get('currency'), "to_currency": total_price_currency})['price']
    
    return total_price