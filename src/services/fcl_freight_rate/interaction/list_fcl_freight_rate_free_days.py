from services.fcl_freight_rate.models.fcl_freight_rate_free_day import FclFreightRateFreeDay
from math import ceil
from fastapi.encoders import jsonable_encoder
from libs.get_filters import get_filters
from libs.get_applicable_filters import get_applicable_filters
import json
from datetime import datetime

possible_direct_filters = ['id', 'port_id', 'country_id', 'trade_id', 'continent_id', 'shipping_line_id', 'service_provider_id', 'importer_exporter_id', 'trade_type', 'free_days_type', 'container_size', 'container_type', 'is_slabs_missing', 'location_id', 'specificity_type', 'previous_days_applicable', 'rate_not_available_entry']
possible_indirect_filters = ['importer_exporter_present', 'active', 'inactive']

def list_fcl_freight_rate_free_days(filters = {}, page_limit = 10, page = 1, pagination_data_required = True, return_query = False):
    query = get_query(page, page_limit)

    if filters:
        if type(filters) != dict: 
            filters = json.loads(filters)
        
        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)
  
        query = get_filters(direct_filters, query, FclFreightRateFreeDay)
        query = apply_indirect_filters(query, indirect_filters)

    if return_query: 
        return { 'list': str(query) } 

    data = jsonable_encoder(list(query.dicts()))
    pagination_data = get_pagination_data(query, page, page_limit, pagination_data_required)
    
    return { 'list': data } | pagination_data

def get_query(page, page_limit):
    query = FclFreightRateFreeDay.select(
        FclFreightRateFreeDay.id,
        FclFreightRateFreeDay.location_id,
        FclFreightRateFreeDay.shipping_line_id,
        FclFreightRateFreeDay.service_provider_id,
        FclFreightRateFreeDay.importer_exporter_id,
        FclFreightRateFreeDay.trade_type,
        FclFreightRateFreeDay.free_days_type,
        FclFreightRateFreeDay.container_size,
        FclFreightRateFreeDay.container_type,
        FclFreightRateFreeDay.free_limit,
        FclFreightRateFreeDay.remarks,
        FclFreightRateFreeDay.slabs,
        FclFreightRateFreeDay.is_slabs_missing,
        FclFreightRateFreeDay.specificity_type,
        FclFreightRateFreeDay.updated_at,
        FclFreightRateFreeDay.previous_days_applicable,
        FclFreightRateFreeDay.shipping_line,
        FclFreightRateFreeDay.location,
        FclFreightRateFreeDay.service_provider,
        FclFreightRateFreeDay.importer_exporter,
        FclFreightRateFreeDay.validity_start,
        FclFreightRateFreeDay.validity_end
    ).order_by(FclFreightRateFreeDay.updated_at.desc(nulls = 'LAST')).paginate(page, page_limit)
    return query


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

def apply_active_filter(query):
    return query.where(FclFreightRateFreeDay.validity_end >= datetime.now())

def apply_inactive_filter(query):
    return query.where( FclFreightRateFreeDay.validity_end < datetime.now())