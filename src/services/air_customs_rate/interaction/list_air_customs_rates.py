from services.air_customs_rate.models.air_customs_rate import AirCustomsRate
from libs.get_filters import get_filters
from libs.get_applicable_filters import get_applicable_filters
from micro_services.client import common
import json

possible_direct_filters = ['id', 'airport_id', 'country_id', 'trade_id', 'continent_id', 'trade_type', 'service_provider_id', 'importer_exporter_id', 'commodity', 'rate_type', 'is_line_items_info_messages_present', 'is_line_items_error_messages_present', 'procured_by_id']

possible_indirect_filters = ['location_ids', 'is_rate_available', 'importer_exporter_present']

def list_air_customs_rates(filters = {}, page_limit = 10, page = 1, sort_by = 'updated_at', sort_type = 'desc', return_query = False, pagination_data_required = False):
    query = get_query(sort_by, sort_type, page, page_limit)
    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)

        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)
  
        query = get_filters(direct_filters, query, AirCustomsRate)
        query = apply_indirect_filters(query, indirect_filters)

    if return_query:
        return {'list': query} 
    
    data = get_data(query)
  
    return {'list': data } 

# def get_query(sort_by, sort_type, page, page_limit):
#   query = AirCustomsRate.select().where(AirCustomsRate.rate_not_available_entry == False).order_by(eval('AirCustomsRate.{}.{}()'.format(sort_by,sort_type))).paginate(page, page_limit)
#   return query
  
# def get_data(query):
#     data = list(query.dicts())

#     for object in data:
#         object['total_price_currency'] = 'INR'
#         object['total_price'] = get_total_price(object['line_items'], object['total_price_currency'])

#     return data

# def apply_indirect_filters(query, filters):
#   for key in filters:
#     apply_filter_function = f'apply_{key}_filter'
#     query = eval(f'{apply_filter_function}(query, filters)')
#   return query

# def apply_location_ids_filter(query, filters):
#     location_ids = filters['location_ids']
#     query = query.where(AirCustomsRate.location_ids.contains(location_ids))
#     return query 

# def apply_importer_exporter_present_filter(query, filters):
#     if filters['importer_exporter_present']:
#         return query.where(AirCustomsRate.importer_exporter_id.is_null(False))
  
#     query = query.where(AirCustomsRate.importer_exporter_id.is_null(True))
#     return query

# def apply_is_rate_available_filter(query, filters):
#     rate_not_available_entry = not filters.get('is_rate_available')
#     query = query.where(AirCustomsRate.rate_not_available_entry == rate_not_available_entry)
#     return query 

# def get_total_price(line_items, total_price_currency):
#     total_price = 0
#     for line_item in line_items:
#         total_price += common.get_money_exchange_for_fcl({"price": line_item.get('price'), "from_currency": line_item.get('currency'), "to_currency": total_price_currency})['price']
    
#     return total_price