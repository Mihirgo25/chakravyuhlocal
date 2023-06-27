from services.fcl_customs_rate.models.fcl_customs_rate import FclCustomsRate
from libs.get_filters import get_filters
from libs.get_applicable_filters import get_applicable_filters
import json
from math import ceil
from micro_services.client import common
from configs.fcl_freight_rate_constants import RATE_TYPES

possible_direct_filters = ['id', 'location_id', 'country_id', 'trade_id', 'continent_id', 'trade_type', 'service_provider_id', 'importer_exporter_id', 'commodity', 'container_type', 'container_size', 'is_customs_line_items_info_messages_present', 'is_customs_line_items_error_messages_present', 'is_cfs_line_items_info_messages_present', 'is_cfs_line_items_error_messages_present', 'procured_by_id', 'rate_type']

possible_indirect_filters = ['location_ids', 'importer_exporter_present', 'is_rate_available']

def list_fcl_customs_rates(filters = {}, page_limit = 10, page = 1, sort_by = 'updated_at', sort_type = 'desc', return_query = False, pagination_data_required = False):
    query = get_query(sort_by, sort_type, page, page_limit)
    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)
        
        if filters.get('rate_type') == 'all':
            filters['rate_type'] = RATE_TYPES

        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)
  
        query = get_filters(direct_filters, query, FclCustomsRate)
        query = apply_indirect_filters(query, indirect_filters)

    if return_query:
        return {'list': query} 
    
    data = get_data(query)
    if pagination_data_required:
        pagination_data = get_pagination_data(query, page, page_limit)
        return {'list': data } | (pagination_data)
    
    return {'list': data }

def get_query(sort_by, sort_type, page, page_limit):
  query = FclCustomsRate.select(
            FclCustomsRate.id,
            FclCustomsRate.location_id,
            FclCustomsRate.trade_type,
            FclCustomsRate.importer_exporter_id,
            FclCustomsRate.service_provider_id,
            FclCustomsRate.commodity,
            FclCustomsRate.container_type,
            FclCustomsRate.container_size,
            FclCustomsRate.customs_line_items,
            FclCustomsRate.customs_line_items_info_messages,
            FclCustomsRate.is_customs_line_items_info_messages_present,
            FclCustomsRate.customs_line_items_error_messages,
            FclCustomsRate.is_customs_line_items_error_messages_present,
            FclCustomsRate.cfs_line_items,
            FclCustomsRate.cfs_line_items_info_messages,
            FclCustomsRate.is_cfs_line_items_info_messages_present,
            FclCustomsRate.cfs_line_items_error_messages,
            FclCustomsRate.is_cfs_line_items_error_messages_present,
            FclCustomsRate.updated_at,
            FclCustomsRate.sourced_by_id,
            FclCustomsRate.procured_by_id,
            FclCustomsRate.importer_exporter,
            FclCustomsRate.service_provider,
            FclCustomsRate.location,
            FclCustomsRate.procured_by,
            FclCustomsRate.sourced_by
  ).order_by(eval('FclCustomsRate.{}.{}()'.format(sort_by,sort_type))).paginate(page, page_limit)
  return query
  
def get_pagination_data(query, page, page_limit):
    total_count = query.count()
    pagination_data = {
        'page': page,
        'total': ceil(total_count/page_limit),
        'total_count': total_count,
        'page_limit': page_limit
        }
    return pagination_data

def get_data(query):
    data = list(query.dicts())
    for object in data:
        if object['customs_line_items']:
            object['total_price_currency'] = object['customs_line_items'][0].get('currency')
        else:
            object['total_price_currency'] = 'INR'
        object['total_price'] = get_total_price(object.get('customs_line_items'), object['total_price_currency'])

    return data

def apply_indirect_filters(query, filters):
  for key in filters:
    apply_filter_function = f'apply_{key}_filter'
    query = eval(f'{apply_filter_function}(query, filters)')
  return query

def apply_location_ids_filter(query, filters):
    location_ids = filters['location_ids']
    query = query.where(FclCustomsRate.location_ids.contains(location_ids))
    return query 

def apply_importer_exporter_present_filter(query, filters):
    if filters['importer_exporter_present']:
        return query.where(FclCustomsRate.importer_exporter_id.is_null(False))
  
    query = query.where(FclCustomsRate.importer_exporter_id.is_null(True))
    return query

def apply_is_rate_available_filter(query, filters):
    rate_not_available_entry = not filters.get('is_rate_available')
    query = query.where(FclCustomsRate.rate_not_available_entry == rate_not_available_entry)
    return query 

def get_total_price(line_items, total_price_currency):
    total_price = 0
    if line_items:
        for line_item in line_items:
            total_price += common.get_money_exchange_for_fcl({"price": line_item.get('price'), "from_currency": line_item.get('currency'), "to_currency": total_price_currency})['price']
    
    return total_price