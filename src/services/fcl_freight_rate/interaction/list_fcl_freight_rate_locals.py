from services.fcl_freight_rate.models.fcl_freight_rate_local import FclFreightRateLocal
from services.fcl_freight_rate.helpers.direct_filters import apply_direct_filters
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_local_agents import list_fcl_freight_rate_local_agents
import json
from datetime import datetime
from micro_services.client import *
from playhouse.shortcuts import model_to_dict

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
                FclFreightRateLocal.procured_by,
                FclFreightRateLocal.sourced_by,
                )
    local_agent_mappings = {}
    port_ids = []
    service_provider_ids = []
    for item in list(query.dicts()):
        port_ids.append(item['port_id'])
        service_provider_ids.append(item['service_provider_id'])

    local_agent_objects = list_fcl_freight_rate_local_agents(filters = {'location_id': list(set(port_ids)), 'service_provider_id': list(set(service_provider_ids))})['list']
    for value in local_agent_objects:
        local_agent_mappings[':'.join([str(value['service_provider_id']), str(value['location_id']), str(value['trade_type'])])] = value

    for result in results.dicts():
        result['line_items'] = result['data'].get('line_items')
        result['detention'] = result['data'].get('detention')
        result['demurrage'] = result['data'].get('demurrage')
        result['plugin'] = result['data'].get('plugin')

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
                if line_item['currency'] != result['total_price_currency']:
                    conversion = common.get_money_exchange_for_fcl({"price":line_item['price'], "from_currency":line_item['currency'], "to_currency":result['total_price_currency']})
                    if 'price' in conversion:
                        total_price += conversion['price']
                else:
                    total_price += line_item['price']
            result['total_price'] = total_price
        result['is_local_agent_rate'] = True if local_agent_mappings.get(':'.join([str(result['service_provider_id'] or ''), str((result.get('port') or {}).get('id') or ''), result['trade_type']])) else False
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
