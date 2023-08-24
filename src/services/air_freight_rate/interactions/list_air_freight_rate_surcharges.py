from services.air_freight_rate.models.air_freight_rate_surcharge import AirFreightRateSurcharge
from libs.json_encoder import json_encoder
from libs.get_filters import get_filters
from libs.get_applicable_filters import get_applicable_filters
from math import ceil
import json
from services.air_freight_rate.constants.air_freight_rate_constants import KOLKATA, EAMS_AIRLINES


possible_direct_filters = ['id','origin_airport_id', 'origin_country_id', 'origin_trade_id', 'origin_continent_id', 'destination_airport_id', 'destination_country_id', 'destination_trade_id', 'destination_continent_id', 'service_provider_id', 'airline_id', 'is_line_items_info_messages_present', 'commodity', 'is_line_items_error_messages_present', 'operation_type','procured_by_id']
possible_indirect_filters = ['location_ids']

def list_air_freight_rate_surcharges(filters = {}, page_limit = 10, page = 1, pagination_data_required=True, return_query = False, sort_by='updated_at', sort_type = 'desc', includes= {}):
    query = get_query(sort_by,sort_type, includes)

    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)
        
        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)
        
        query = get_filters(direct_filters, query, AirFreightRateSurcharge)
        query = apply_indirect_filters(query, indirect_filters)
   
    if return_query: 
        return { 'list': query }
    
    pagination_data = get_pagination_data(query,page, page_limit, pagination_data_required)
    query = query.paginate(page, page_limit)
    data = json_encoder(list(query.dicts()))
    data = get_eligible_charge_codes(data)
    return { 'list': data } | (pagination_data)

def get_eligible_charge_codes(surcharges):
    for surcharge in surcharges:
        not_required_charge_codes = ['EAMS','EHAMS','HAMS']
        if surcharge['origin_airport_id'] == KOLKATA and surcharge['airline_id'] in EAMS_AIRLINES:
            not_required_charge_codes = ['AMS','EHAMS','HAMS']
        new_line_items = []
        for line_item in surcharge['line_items']:
            if line_item['code'] in not_required_charge_codes:
                continue
            new_line_items.append(line_item)
        surcharge['line_items'] = new_line_items
    return surcharges

def get_query(sort_by,sort_type, includes):
    if includes:
        if type(includes) != dict:
            includes =json.loads(includes)
            
    requred_fields = list(includes.keys()) if includes else list(AirFreightRateSurcharge._meta.fields.keys())
    fields = [getattr(AirFreightRateSurcharge, key) for key in requred_fields] 
    
    query = AirFreightRateSurcharge.select(*fields).where(~(AirFreightRateSurcharge.rate_not_available_entry)).order_by(eval('AirFreightRateSurcharge.{}.{}()'.format(sort_by,sort_type)))
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


def apply_location_ids_filter(query,filters):
    locations_ids = filters['location_ids']
    query = query.where(AirFreightRateSurcharge.destination_location_ids.contains(locations_ids))
    return query 