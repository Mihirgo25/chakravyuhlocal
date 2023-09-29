from services.air_freight_rate.models.air_freight_rate_local import AirFreightRateLocal
from libs.json_encoder import json_encoder
from libs.get_filters import get_filters
from libs.get_applicable_filters import get_applicable_filters
from math import ceil
import json
from libs.apply_eligible_lsp_filters import apply_eligible_lsp_filters


possible_direct_filters = ['id', 'airport_id', 'country_id', 'trade_id', 'continent_id', 'trade_type', 'commodity', 'airline_id', 'service_provider_id', 'is_line_items_info_messages_present', 'is_line_items_error_messages_present', 'rate_type','procured_by_id','importer_exporter_id']

possible_indirect_filters = ['location_ids','exclude_rate_types','exclude_airline_id']

def list_air_freight_rate_locals(filters={},page_limit=10,page=1,
sort_by='updated_at',pagination_data_required=True,sort_type='desc',return_query=False,return_count = False):
    
    query=get_query(sort_by,sort_type)

    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)
        
        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)
        
        query = get_filters(direct_filters, query, AirFreightRateLocal)
        
        query = apply_indirect_filters(query, indirect_filters)
    
    if not filters or not 'service_provider_id' in filters:
        query = apply_eligible_lsp_filters(query,AirFreightRateLocal,'air_freight')

    if return_query: 
        return { 'list': query }
    if return_count:
        return {'total_count':query.count()}
    pagination_data=get_pagination_data(query,page,page_limit,pagination_data_required)
    query = query.paginate(page, page_limit)
    data = json_encoder(list(query.dicts()))

    return { 'list': data } | (pagination_data)

def get_query(sort_by,sort_type):
    
    query=AirFreightRateLocal.select().where(~(AirFreightRateLocal.rate_not_available_entry)).order_by(eval('AirFreightRateLocal.{}.{}()'.format(sort_by,sort_type)))
    return query
    

def apply_location_ids_filter(query,filters):
    location_ids = filters['location_ids']
    query = query.where(
        AirFreightRateLocal.location_ids.contains(location_ids)
    )
    return query
    
def apply_indirect_filters(query,filters):
    
    for key in filters:
        if key in possible_indirect_filters:
            apply_filter_function = f'apply_{key}_filter'
            query = eval(f'{apply_filter_function}(query, filters)')
    return query

def apply_exclude_rate_types_filter(query, filters):
  query=query.where(~AirFreightRateLocal.rate_type << filters['exclude_rate_types'])
  return query

def apply_exclude_airline_id_filter(query, filters):
  airline_ids = filters['exclude_airline_id']
  query=query.where(~AirFreightRateLocal.airline_id << airline_ids)
  return query

def get_pagination_data(query, page, page_limit, pagination_data_required):
    if not pagination_data_required:
        return {}
    
    total_count = query.count()
    return {
        "page": page,
        "total": ceil(total_count/page_limit),
        "total_count": total_count,
        "page_limit": page_limit
    }
# where need to change column name or front end
# object[:organization_detail] = service_objects[:organization][object[:service_provider_id].to_sym] rescue nil
