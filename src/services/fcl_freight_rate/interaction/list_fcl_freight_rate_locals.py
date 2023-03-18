from services.fcl_freight_rate.models.fcl_freight_rate_local import FclFreightRateLocal
from services.fcl_freight_rate.models.fcl_freight_rate_audit import FclFreightRateAudit
from services.fcl_freight_rate.helpers.find_or_initialize import apply_direct_filters
from operator import itemgetter
import json
from datetime import datetime
from rails_client import client
from playhouse.shortcuts import model_to_dict
from math import ceil
import time

possible_direct_filters = ['id', 'port_id', 'country_id', 'trade_id', 'continent_id', 'shipping_line_id', 'service_provider_id', 'trade_type', 'container_size', 'container_type', 'is_line_items_error_messages_present', 'is_line_items_info_messages_present', 'main_port_id']
possible_indirect_filters = ['is_detention_missing', 'is_demurrage_missing', 'is_plugin_missing', 'location_ids', 'commodity', 'procured_by_id', 'is_rate_available', 'updated_at_greater_than', 'updated_at_less_than']

def list_fcl_freight_rate_locals(filters = {}, page_limit =10, page=1, sort_by='updated_at', sort_type='desc', return_query=False): 
    query = get_query(sort_by, sort_type, page, page_limit)

    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)

        query = apply_direct_filters(query, filters, possible_direct_filters, FclFreightRateLocal)
        query = apply_indirect_filters(query, filters)   
    
    if return_query:
        items = [model_to_dict(item) for item in query.execute()]
        return {'list': items}

    data = get_data(query)
    
    return { 'list': data }

    
def get_query(sort_by, sort_type, page, page_limit):
    query = FclFreightRateLocal.select().order_by(eval('FclFreightRateLocal.{}.{}()'.format(sort_by,sort_type))).paginate(page, page_limit)
    return query

def get_data(query):
    data = []
    results = query.select(FclFreightRateLocal.id, 
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
                FclFreightRateLocal.is_local_agent_rate,
                FclFreightRateLocal.procured_by,
                FclFreightRateLocal.sourced_by,
                )

    for result in results.dicts():
        result['line_items'] = result['data']['line_items']
        result['detention'] = result['data']['detention']
        result['demurrage'] = result['data']['demurrage']
        result['plugin'] = result['data']['plugin']

        if result['detention']:
            if 'free_limit' in result['detention']:
                result['is_detention_missing'] = False if result['detention']['free_limit'] else True
        else:
            result['is_detention_missing'] = True
  
        if result['trade_type'] == 'import':
            result['is_demurrage_missing'] = not result['demurrage']['free_limit'] if result['demurrage'] else True
        
        if result['container_type'] == 'refer':
            result['is_plugin_missing'] =  not result['plugin']['free_limit'] if result['plugin'] else True
        
        result['total_price'] = 0
        if result['line_items']:
            result['total_price_currency'] = result['line_items'][0].get('currency')    
        else:
            result['total_price_currency'] = None 

        if result['total_price_currency']:
            total_price = 0
            for line_item in result['line_items']:
                conversion = client.ruby.get_money_exchange_for_fcl({"price":line_item['price'], "from_currency":line_item['currency'], "to_currency":result['total_price_currency']})
                if 'price' in conversion:
                    total_price += conversion['price']
            result['total_price'] = total_price
    
        data.append(result)
    return data

def apply_indirect_filters(query, filters):
    for key in filters:
        if key in possible_indirect_filters:
            apply_filter_function = f'apply_{key}_filter'
            query = eval(f'{apply_filter_function}(query, filters)')
    return query

def apply_is_detention_missing_filter(query, filters):
    query = query.where(FclFreightRateLocal.is_detention_slabs_missing.in_([None,True]))
    return query

def apply_is_demurrage_missing_filter(query, filters):
    query = query.where(FclFreightRateLocal.is_demurrage_slabs_missing.in_([None,True]))
    return query

def apply_is_plugin_missing_filter(query, filters):
    query = query.where(FclFreightRateLocal.is_plugin_slabs_missing.in_([None,True]))
    return query

def apply_is_rate_available_filter(query, filters):
    if filters['is_rate_available'] == False: 
        query = query.where(FclFreightRateLocal.rate_not_available_entry == True)
    else:
        query = query.where((FclFreightRateLocal.rate_not_available_entry == None) | (FclFreightRateLocal.rate_not_available_entry == False))
    return query

def apply_location_ids_filter(query, filters):
    location_ids = filters['location_ids']
    query = query.where(FclFreightRateLocal.location_ids.contains(location_ids))
    return query

def apply_commodity_filter(query, filters):
    query = query.where((FclFreightRateLocal.commodity == None) | (FclFreightRateLocal.commodity == filters['commodity']))
    return query

def apply_updated_at_greater_than_filter(query, filters):
    query = query.where(FclFreightRateLocal.updated_at >= datetime.strptime(filters['updated_at_greater_than'], '%Y-%m-%d'))
    return query

def apply_updated_at_less_than_filter(query, filters):
    query = query.where(FclFreightRateLocal.updated_at <= datetime.strptime(filters['updated_at_less_than'], '%Y-%m-%d'))
    return query

def apply_procured_by_id_filter(query, filters):
    query = query.where(FclFreightRateLocal.procured_by_id == filters['procured_by_id'])
    return query