from services.fcl_freight_rate.models.fcl_freight_rate_audits import FclFreightRateAudit
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.models.fcl_freight_rate_seasonal_surcharge import FclFreightRateSeasonalSurcharge
from services.fcl_freight_rate.interaction.list_fcl_freight_rates import remove_unexpected_filters
import concurrent.futures
from rails_client import client
from math import ceil
from datetime import datetime
from operator import attrgetter
from peewee import JOIN 
from playhouse.shortcuts import model_to_dict
from peewee import Case, SQL 

possible_direct_filters = ['object_type']
possible_indirect_filters = ['created_at_greater_than']
possible_hash_filters = {
    'fcl_freight_rate': {
    'direct': ['origin_port_id', 'origin_main_port_id', 'destination_port_id', 'destination_main_port_id', 'container_size', 'container_type', 'commodity', 'shipping_line_id', 'rate_not_available_entry', 'service_provider_id'],
    'indirect': ['validity_start_less_than_equal_to', 'validity_end_greater_than_equal_to']
    },
    'fcl_freight_rate_seasonal_surcharge': {
    'direct': ['origin_port_id', 'origin_country_id', 'origin_trade_id', 'origin_continent_id', 'destination_port_id', 'destination_country_id', 'destination_trade_id', 'destination_continent_id', 'shipping_line_id', 'service_provider_id', 'container_size', 'container_type', 'code', 'origin_location_id', 'destination_location_id'],
    'indirect': ['validity_start_less_than_equal_to', 'validity_end_greater_than_equal_to']
    }
}

def list_fcl_freight_rate_audits(filters, sort_by, sort_type, page, page_limit, pagination_data_required, user_data_required):
    filters = remove_unexpected_filters(filters, possible_direct_filters, possible_indirect_filters)
    query = get_query(sort_by, sort_type, page, page_limit)
    query = apply_direct_filters(query, filters)
    query = apply_indirect_filters(query, filters)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(eval(method_name), query, page, page_limit, pagination_data_required) for method_name in ['get_data', 'get_pagination_data']]
        results = {}
        for future in futures:
            result = future.result()
            results.update(result)
        
    method_responses = results
    data = method_responses['get_data']
    pagination_data = method_responses['get_pagination_data']

    return {'list': data } | (pagination_data)

def get_query(sort_by, sort_type, page, page_limit):
    query = FclFreightRateAudit.select().order("FclFreightRateAudit.{}.{}()".format(sort_by,sort_type)).paginate(page, page_limit)
    return query

def get_pagination_data(query, page, page_limit, pagination_data_required, user_data_required):
    if not pagination_data_required:
        return {'get_pagination_data':{}} 

    params = {
      'page': page,
      'total': ceil(query.count()/page_limit),
      'total_count': query.count(),
      'page_limit': page_limit
    }
    return {'get_pagination_data':params}

def get_data(query, page, page_limit, pagination_data_required, user_data_required):
    data = [model_to_dict(item) for item in query.execute()]
    data = add_service_objects(data, user_data_required)
    return data

def add_service_objects(data, user_data_required):
    objects = []

    if user_data_required: 
        user_ids = list(set(filter(None, [item for sublist in [(d.get('sourced_by_id'), d.get('procured_by_id'), d.get('performed_by_id')) for d in data] for item in sublist])))
        objects.append({
            'name': 'user',
            'filters': { 'id': user_ids },
            'fields': ['id', 'name', 'email']
        })
        objects.append({
            'name': 'rate_sheet', 
            'filters': { 'id': list(set(filter(None, [d.get('rate_sheet_id') for d in data])))},
            'fields': ['serial_id', 'file_name', 'created_at', 'updated_at']
        })
    
    if not objects:
        return data 

    service_objects = client.ruby.get_multiple_service_objects_data_for_fcl({'objects': objects})

    new_data = []
    for object in data:
        object['sourced_by']   = service_objects['user'][object['sourced_by_id']] if 'user' in service_objects and object.get('sourced_by_id') in service_objects['user'] else None
        object['procured_by']  = service_objects['user'][object['procured_by_id']] if 'user' in service_objects and object.get('procured_by_id') in service_objects['user'] else None
        object['performed_by'] = service_objects['user'][object['performed_by_id']] if 'user' in service_objects and object.get('performed_by_id') in service_objects['user'] else None
        object['rate_sheet'] = service_objects['rate_sheet'][object['rate_sheet_id']] if 'rate_sheet' in service_objects and object.get('rate_sheet_id') in service_objects['rate_sheet'] else None
        new_data.append(object)
    return new_data

def apply_direct_filters(query, filters):
    for key in filters:
        if key in possible_direct_filters:
            query = query.select().where(attrgetter(key)(FclFreightRateAudit) == filters[key])
    return query

def apply_indirect_filters(query, filters):
    for key in filters:
        if key in possible_indirect_filters:
            apply_filter_function = f'apply_{key}_filter'
            query = eval(f'{apply_filter_function}(query, filters)')
    return query

def apply_hash_filters(query, filters):
    hash_filters = {key:value for key,value in filters.items() if key in possible_hash_filters.keys()}

    for filter in hash_filters:
        query = eval("apply_{}_filter(query, filters)".format(filter))
        if possible_hash_filters[filter]['direct']:
            query = eval("apply_{}_direct_filter(query,filters)".format(filter))  
        if possible_hash_filters[filter]['indirect']:
            query = apply_hash_indirect_filters(query, filter, filters) 
    return query

def apply_hash_indirect_filters(query, filter, filters):
    filter = 'fcl_freight_rate'
    filters[filter]['indirect'] = {'validity_start_from' : '2023-02-10'}
    indirect_filters = {key:value for key,value in filters[filter]['indirect'].items() if key in possible_hash_filters[filter]['indirect']}
    for indirect_filter in indirect_filters:
        query = eval("apply_{}_{}_filter(query,filters)".format(filter,indirect_filter))
        return query

def apply_created_at_greater_than_filter(query, filters):
    query = query.where(FclFreightRateAudit.created_at > datetime.strptime(filters['created_at'], '%Y-%m-%d'))
    return query

def apply_fcl_freight_rate_filter(query, filters):
    query = query.select(FclFreightRate).join(FclFreightRate, JOIN.INNER, on=(FclFreightRateAudit.object_id == FclFreightRate.id)).where(FclFreightRateAudit.object_type == 'FclFreightRate')
    return query

def apply_fcl_freight_rate_direct_filter(query, filters):
    direct_filters = {key:value for key,value in filters['fcl_freight_rate']['direct'].items() if key in possible_hash_filters['fcl_freight_rate']['direct']}
    for direct_filter in direct_filters:
        query = query.where(attrgetter(direct_filter)(FclFreightRate) == direct_filters[direct_filter])
    return query

def apply_fcl_freight_rate_seasonal_surcharge_filter(query, filters):
    query = query.select(FclFreightRateSeasonalSurcharge).join(FclFreightRateSeasonalSurcharge, JOIN.INNER, on = (FclFreightRateAudit.object_id == FclFreightRateSeasonalSurcharge.id)).where(FclFreightRateAudit.object_type == 'FclFreightRateSeasonalSurcharge')
    return query

def apply_fcl_freight_rate_seasonal_surcharge_direct_filter(query, filters):
    direct_filters = {key:value for key,value in filters['fcl_freight_rate_seasonal_surcharge']['direct'].items() if key in possible_hash_filters['fcl_freight_rate_seasonal_surcharge']['direct']}
    for direct_filter in direct_filters:
        query = query.where(attrgetter(direct_filter)(FclFreightRateSeasonalSurcharge) == direct_filters[direct_filter])
    return query

def apply_fcl_freight_rate_validity_start_less_than_equal_to_filter(query, filters):
    validity_start_less_than_equal_to = filters["fcl_freight_rate"]["validity_start_less_than_equal_to"]
    case_query = (
        Case(
            None, (
                (
                    SQL("FclFreightRateAudit.data ->> 'validity_start' like '%/%/%'"),
                    datetime.strptime(SQL("FclFreightRateAudit.data ->> 'validity_start'"), "DD/MM/YY")
                ),
                (
                    SQL("FclFreightRateAudit.data ->> 'validity_start' like '%-%-____'"),
                    datetime.strptime(SQL("FclFreightRateAudit.data ->> 'validity_start'"), "DD-MM-YYYY")
                ),
            ),
            datetime.strptime(SQL("FclFreightRateAudit.data ->> 'validity_start'"), "YYYY-MM-DD")
        )
    ).alias("case_query")
    return query.where(case_query <= datetime.strptime(validity_start_less_than_equal_to, "YYYY-MM-DD"))

def apply_fcl_freight_rate_validity_start_greater_than_equal_to_filter(query, filters):
    validity_start_greater_than_equal_to = filters["fcl_freight_rate"]["validity_start_greater_than_equal_to"]
    case_query = (
        Case(
            None, (
                (
                    SQL("FclFreightRateAudit.data ->> 'validity_start' like '%/%/%'"),
                    datetime.strptime(SQL("FclFreightRateAudit.data ->> 'validity_start'"), "DD/MM/YY")
                ),
                (
                    SQL("FclFreightRateAudit.data ->> 'validity_start' like '%-%-____'"),
                    datetime.strptime(SQL("FclFreightRateAudit.data ->> 'validity_start'"), "DD-MM-YYYY")
                ),
            ),
            datetime.strptime(SQL("FclFreightRateAudit.data ->> 'validity_start'"), "YYYY-MM-DD")
        )
    ).alias("case_query")
    return query.where(case_query >= datetime.strptime(validity_start_greater_than_equal_to, "YYYY-MM-DD"))


def apply_fcl_freight_rate_seasonal_surcharge_validity_start_less_than_equal_to_filter(query, filters):
    query = query.where(FclFreightRateSeasonalSurcharge.validity_start <= datetime.strptime(filters['fcl_freight_rate_seasonal_surcharge']['validity_start_less_than_equal_to'], '%Y-%m-%d'))
    return query

def apply_fcl_freight_rate_seasonal_surcharge_validity_end_greater_than_equal_to_filter(query, filters):
    query = query.where(FclFreightRateSeasonalSurcharge.validity_end >= datetime.strptime(filters['fcl_freight_rate_seasonal_surcharge']['validity_end_greater_than_equal_to'], '%Y-%m-%d'))
    return query