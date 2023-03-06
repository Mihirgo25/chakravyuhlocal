from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.models.fcl_freight_rate_local import FclFreightRateLocal
from services.fcl_freight_rate.models.fcl_freight_rate_audits import FclFreightRateAudit
from services.fcl_freight_rate.interaction.list_fcl_freight_rates import remove_unexpected_filters
from operator import attrgetter, itemgetter
from datetime import datetime
from rails_client import client
from playhouse.shortcuts import model_to_dict
from math import ceil

possible_direct_filters = ['id', 'port_id', 'country_id', 'trade_id', 'continent_id', 'shipping_line_id', 'service_provider_id', 'trade_type', 'container_size', 'container_type', 'is_line_items_error_messages_present', 'is_line_items_info_messages_present', 'main_port_id']
possible_indirect_filters = ['is_detention_missing', 'is_demurrage_missing', 'is_plugin_missing', 'location_ids', 'commodity', 'procured_by_id', 'is_rate_available', 'updated_at_greater_than', 'updated_at_less_than']

def list_fcl_freight_rate_locals(filters, page_limit, page, sort_by, sort_type, pagination_data_required, return_query):
    filters = remove_unexpected_filters(filters, possible_direct_filters, possible_direct_filters)
    query = get_query(sort_by, sort_type, page, page_limit)
    query = apply_direct_filters(query, filters)
    query = apply_indirect_filters(query, filters)
    
    if return_query:
        items = [model_to_dict(item) for item in query]
        return {'list': items}

    data = get_data(query)
    pagination_data = get_pagination_data(query, page, page_limit, pagination_data_required)
    
    return ({ 'list': data } | (pagination_data))

    
def get_query(sort_by, sort_type, page, page_limit):
    query = FclFreightRateLocal.select().order_by(eval('FclFreightRateLocal.{}.{}()'.format(sort_by,sort_type))).paginate(page, page_limit)
    return query

def get_pagination_data(query, page, page_limit, pagination_data_required):
    if not pagination_data_required:
        return {}

    params = {
      'page': page,
      'total': ceil(query.count()/page_limit),
      'total_count': query.count(),
      'page_limit': page_limit
    }
    return params

def get_data(query):
    data = []

    results = query.select(FclFreightRateLocal.id, FclFreightRateLocal.port_id, FclFreightRateLocal.main_port_id, FclFreightRateLocal.shipping_line_id, FclFreightRateLocal.service_provider_id, FclFreightRateLocal.trade_type, FclFreightRateLocal.container_size, FclFreightRateLocal.container_type, FclFreightRateLocal.commodity, FclFreightRateLocal.selected_suggested_rate_id, FclFreightRateLocal.is_line_items_error_messages_present,FclFreightRateLocal.line_items_error_messages,FclFreightRateLocal.is_line_items_info_messages_present,FclFreightRateLocal.line_items_info_messages,FclFreightRateLocal.data,FclFreightRateLocal.created_at,FclFreightRateLocal.updated_at).dicts()
    ids = list(map(itemgetter('id'), results))
    rate_audits = FclFreightRateAudit.select().where(FclFreightRateAudit.object_id.in_(ids), FclFreightRateAudit.object_type == 'FclFreightRateLocal')
    
    for result in results:
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
        result['total_price_currency'] = result['line_items'][0].get('currency')

        rate_audit = [audit for audit in rate_audits if audit['object_id'] == result['id']]

        if rate_audit:
            rate_audit = max(rate_audit, key = lambda x: x['created_at'])
            result['sourced_by_id'] = rate_audit.get('sourced_by_id')
            result['procured_by_id'] = rate_audit.get('procured_by_id')
        else:
            rate_audit = None
            result['sourced_by_id'] = None
            result['procured_by_id'] = None        

        if result['total_price_currency']:
            total_price = 0
            for line_item in result['line_items']:
                conversion = client.ruby.get_money_exchange_for_fcl({"price":line_item['price'], "from_currency":line_item['currency'], "to_currency":result['total_price_currency']})
                if 'price' in conversion:
                    total_price += conversion['price']
            result['total_price'] = total_price

        data.append(result)

    data = add_service_objects(data)
    return data

def add_service_objects(data):
    if data.count == 0:
        return data 

    params = {'objects': [
      {
        'name': 'operator',
        'filters': {'id': list(set(str(item["shipping_line_id"]) for item in data))},
        'fields': ['id', 'business_name', 'short_name', 'logo_url']
      },
      {
        'name': 'location',
        'filters':{"id": list(set(item for sublist in [[str(item["port_id"]), str(item["main_port_id"])] for item in data] for item in sublist))},
        'fields': ['id', 'name', 'display_name', 'port_code', 'type', 'is_icd', 'country_id']
      },
      {
        'name': 'organization',
        'filters' : {"id": list(set(item for sublist in [str(item["service_provider_id"]) for item in data] for item in sublist))},
        'fields': ['id', 'business_name', 'short_name'],
        'extra_params': {'add_service_objects_required': False }
      },
      {
        'name': 'fcl_freight_rate_local_agent',
        'filters': {'location_id': list(set(str(item['port_id']) for item in data)), 'service_provider_id': list(set(str(item["service_provider_id"]) for item in data))},
        'fields': ['service_provider_id', 'location_id', 'trade_type'],
        'extra_params': { 'add_service_objects_required': False }
      },
      {
        'name': 'user',
        'filters': {"id": list(set(item for sublist in [[str(item["procured_by_id"]), str(item["sourced_by_id"])] for item in data] for item in sublist if item is not None))},
        'fields': ['id', 'name', 'email']
      }
    ]}

    service_objects = client.ruby.get_multiple_service_objects_data_for_fcl(params)
    local_agent_mappings = {} 

    if service_objects['fcl_freight_rate_local_agent']:
        for key, value in service_objects['fcl_freight_rate_local_agent'].items():
            local_agent_mappings[':'.join([service_objects['fcl_freight_rate_local_agent'][key]['service_provider_id'], service_objects['fcl_freight_rate_local_agent'][key]['location_id'], service_objects['fcl_freight_rate_local_agent'][key]['trade_type']])] = value
    
    new_data = []
    for object in data:
        object['shipping_line'] = service_objects['operator'][str(object['shipping_line_id'])] if ('operator' in service_objects) and (str(object.get('shipping_line_id')) in service_objects['operator']) else None 
        object['port'] = service_objects['location'][str(object['port_id'])] if ('location' in service_objects) and (str(object.get('port_id')) in service_objects['location']) else None
        if object['main_port_id']:
            object['main_port'] = service_objects['location'][str(object['main_port_id'])] if ('location' in service_objects) and (str(object.get('main_port_id')) in service_objects['location']) else None
        else:
            object['main_port'] = None
        object['service_provider'] = service_objects['organization'][str(object['service_provider_id'])] if 'organization' in service_objects and str(object.get('service_provider_id')) in service_objects['organization'] else None
        object['is_local_agent_rate'] = True if local_agent_mappings.get(':'.join([str(object['service_provider_id']), object['port']['id'], object['trade_type']])) else False
        object['procured_by'] = service_objects['user'][str(object['procured_by_id'])] if 'user' in service_objects and str(object.get('procured_by_id')) in service_objects['user'] else None
        object['sourced_by'] = service_objects['user'][str(object['sourced_by_id'])] if 'user' in service_objects and str(object.get('sourced_by_id')) in service_objects['user'] else None
        new_data.append(object)  

    return new_data
    
def apply_direct_filters(query, filters):  
    for key in filters:
        if key in possible_direct_filters:
            query = query.select().where(attrgetter(key)(FclFreightRateLocal) == filters[key])
    return query

def apply_indirect_filters(query, filters):
    for key in filters:
        if key in possible_indirect_filters:
            apply_filter_function = f'apply_{key}_filter'
            query = eval(f'{apply_filter_function}(query, filters)')
    return query

def apply_is_detention_missing_filter(query, filters):
    query = query.where((FclFreightRateLocal.is_detention_slabs_missing == None) | (FclFreightRateLocal.is_detention_slabs_missing == True))
    return query

def apply_is_demurrage_missing_filter(query, filters):
    query = query.where((FclFreightRateLocal.is_demurrage_slabs_missing == None) | (FclFreightRateLocal.is_demurrage_slabs_missing == True))
    return query

def apply_is_plugin_missing_filter(query, filters):
    query = query.where((FclFreightRateLocal.is_plugin_slabs_missing == None) | (FclFreightRateLocal.is_plugin_slabs_missing == True))
    return query

def apply_is_rate_available_filter(query, filters):
    if filters['is_rate_available'] == False: 
        query = query.where(FclFreightRateLocal.rate_not_available_entry == True)
    else:
        query = query.where((FclFreightRateLocal.rate_not_available_entry == None) | (FclFreightRateLocal.rate_not_available_entry == False))
    
    return query

def apply_location_ids_filter(query, filters):
    locations_ids = filters['location_ids']
    query = query.where(FclFreightRateLocal.location_ids.in_(locations_ids))
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
    query = query.select().join(FclFreightRateAudit, on = ((FclFreightRate.id == FclFreightRateAudit.object_id) and (FclFreightRateAudit.seqnum == 1))).where(FclFreightRateAudit.object_type == 'FclFreightRate', FclFreightRateAudit.procured_by_id == filters['procured_by_id'])
    return query