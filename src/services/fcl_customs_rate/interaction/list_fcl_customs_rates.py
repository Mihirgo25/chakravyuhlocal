from services.fcl_customs_rate.models.fcl_customs_rate import FclCustomsRate
from libs.get_filters import get_filters
from libs.get_applicable_filters import get_applicable_filters
import json

possible_direct_filters = ['id', 'location_id', 'country_id', 'trade_id', 'continent_id', 'trade_type', 'service_provider_id', 'importer_exporter_id', 'commodity', 'container_type', 'container_size', 'is_customs_line_items_info_messages_present', 'is_customs_line_items_error_messages_present', 'is_cfs_line_items_info_messages_present', 'is_cfs_line_items_error_messages_present', 'procured_by_id']

possible_indirect_filters = ['location_ids', 'importer_exporter_present', 'is_rate_available']

def list_fcl_customs_rates(filters = {}, page_limit = 10, page = 1, sort_by = 'updated_at', sort_type = 'desc', return_query = False, pagination_data_required = False):
    query = get_query(sort_by, sort_type, page, page_limit)
    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)

        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)
  
        query = get_filters(direct_filters, query, FclCustomsRate)
        query = apply_indirect_filters(query, indirect_filters)

    if return_query:
        return {'list': query} 
    
    data = get_data(query)
  
    return {'list': data } 

def get_query(sort_by, sort_type, page, page_limit):
  query = FclCustomsRate.select().order_by(eval('FclCustomsRate.{}.{}()'.format(sort_by,sort_type))).paginate(page, page_limit)
  return query
  
def get_data(query):
    data = list(query.dicts())

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