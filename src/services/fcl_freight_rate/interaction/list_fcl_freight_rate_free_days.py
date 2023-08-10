from services.fcl_freight_rate.models.fcl_freight_rate_free_day import FclFreightRateFreeDay
from math import ceil
from libs.json_encoder import json_encoder
from libs.get_filters import get_filters
from libs.get_applicable_filters import get_applicable_filters
import json
from datetime import datetime

possible_direct_filters = ['id', 'port_id', 'country_id', 'trade_id', 'continent_id', 'shipping_line_id', 'service_provider_id', 'importer_exporter_id', 'trade_type', 'free_days_type', 'container_size', 'container_type', 'is_slabs_missing', 'location_id', 'specificity_type', 'previous_days_applicable', 'rate_not_available_entry']
possible_indirect_filters = ['importer_exporter_present', 'active', 'inactive']
LIST_FIELDS = ['id', 'location_id', 'shipping_line_id', 'service_provider_id', 'importer_exporter_id', 'trade_type', 'free_days_type', 'container_size', 'container_type', 'free_limit', 'remarks', 'slabs', 'is_slabs_missing', 'specificity_type', 'updated_at', 'previous_days_applicable', 'shipping_line', 'location', 'service_provider', 'importer_exporter', 'validity_start', 'validity_end']

def list_fcl_freight_rate_free_days(filters = {}, page_limit = 10, page = 1, pagination_data_required = True, return_query = False,includes = {}):
    query = get_query(includes)

    if filters:
        if type(filters) != dict: 
            filters = json.loads(filters)
        
        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)
  
        query = get_filters(direct_filters, query, FclFreightRateFreeDay)
        query = apply_indirect_filters(query, indirect_filters)

    pagination_data = get_pagination_data(query, page, page_limit, pagination_data_required)
    
    if page_limit:
        query = query.paginate(page, page_limit)

    if return_query: 
        return { 'list': str(query) } 

    data = json_encoder(list(query.dicts()))

    return { 'list': data } | pagination_data

def get_query(includes):
    if includes:
        if type(includes) != dict: 
            includes = json.loads(includes)
            
    required_fields =  list(includes.keys()) if includes else LIST_FIELDS
    
    fields =  [getattr(FclFreightRateFreeDay, key) for key in required_fields]
            
    query = FclFreightRateFreeDay.select(*fields).order_by(FclFreightRateFreeDay.updated_at.desc(nulls = 'LAST'))
    return query


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

def apply_indirect_filters(query, filters):
    for key in filters:
        if key in possible_indirect_filters:
            apply_filter_function = f'apply_{key}_filter'
            query = eval(f'{apply_filter_function}(query, filters)')
    return query

def apply_importer_exporter_present_filter(query, filters):
    if filters['importer_exporter_present'] == True:
        return query.where(FclFreightRateFreeDay.importer_exporter_id != None)

    query = query.where(FclFreightRateFreeDay.importer_exporter_id == None)
    return query

def apply_active_filter(query,filters):
    return query.where(FclFreightRateFreeDay.validity_end >= datetime.now())

def apply_inactive_filter(query,filters):
    return query.where( FclFreightRateFreeDay.validity_end < datetime.now())