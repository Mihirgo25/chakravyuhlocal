from services.fcl_freight_rate.models.fcl_freight_rate_audit import FclFreightRateAudit
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.models.fcl_freight_rate_seasonal_surcharge import FclFreightRateSeasonalSurcharge
from libs.get_filters import get_filters
from libs.get_applicable_filters import get_applicable_filters
import concurrent.futures
from operator import attrgetter
from math import ceil
from datetime import datetime
import json
from peewee import Case, fn, JOIN

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

def list_fcl_freight_rate_audits(filters = {}, page_limit = 10, page = 1, sort_by = 'updated_at', sort_type = 'desc', pagination_data_required = True, user_data_required = False):
    query = get_query(sort_by, sort_type, page, page_limit)
    
    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)

        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)
  
        query = get_filters(direct_filters, query, FclFreightRateAudit)
        query = apply_indirect_filters(query, indirect_filters)
        query = apply_hash_filters(query, filters)

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(eval(method_name), query, page, page_limit, pagination_data_required, user_data_required) for method_name in ['get_data', 'get_pagination_data']]
        results = {}
        for future in futures:
            result = future.result()
            results.update(result)
        
    data = results['get_data']
    pagination_data = results['get_pagination_data']

    return {'list': data } | (pagination_data)

def get_query(sort_by, sort_type, page, page_limit):
    query = FclFreightRateAudit.select().order_by(eval("FclFreightRateAudit.{}.{}()".format(sort_by,sort_type))).paginate(page, page_limit)
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
    data = []
    for item in query.dicts():
        try:
            item['procured_by'] = item.object_id.procured_by
            item['sourced_by'] = item.object_id.sourced_by
        except:
            item['procured_by'] = None
            item['sourced_by'] = None
        data.append(item)
    return {'get_data' : data}

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
    indirect_filters = {key:value for key,value in filters[filter].items() if key in possible_hash_filters[filter]['indirect']}
    for indirect_filter in indirect_filters:
        query = eval("apply_{}_{}_filter(query,filters)".format(filter,indirect_filter))
        return query

def apply_created_at_greater_than_filter(query, filters):
    query = query.where(FclFreightRateAudit.created_at.cast('date') > datetime.strptime(filters['validity_created_at_greater_than'],'%Y-%m-%dT%H:%M:%S.%fz').date())
    return query

def apply_fcl_freight_rate_filter(query, filters):
    query = query.select().join(FclFreightRate, JOIN.INNER, on=(FclFreightRateAudit.object_id == FclFreightRate.id)).where(FclFreightRateAudit.object_type == 'FclFreightRate')
    return query

def apply_fcl_freight_rate_direct_filter(query, filters):
    direct_filters = {key:value for key,value in filters['fcl_freight_rate'].items() if key in possible_hash_filters['fcl_freight_rate']['direct']}
    for direct_filter in direct_filters:
        query = query.where(attrgetter(direct_filter)(FclFreightRate) == direct_filters[direct_filter])
    return query

def apply_fcl_freight_rate_seasonal_surcharge_filter(query, filters):
    query = query.select(FclFreightRateSeasonalSurcharge).join(FclFreightRateSeasonalSurcharge, JOIN.INNER, on = (FclFreightRateAudit.object_id == FclFreightRateSeasonalSurcharge.id)).where(FclFreightRateAudit.object_type == 'FclFreightRateSeasonalSurcharge')
    return query

def apply_fcl_freight_rate_seasonal_surcharge_direct_filter(query, filters):
    direct_filters = {key:value for key,value in filters['fcl_freight_rate_seasonal_surcharge'].items() if key in possible_hash_filters['fcl_freight_rate_seasonal_surcharge']['direct']}
    for direct_filter in direct_filters:
        query = query.where(attrgetter(direct_filter)(FclFreightRateSeasonalSurcharge) == direct_filters[direct_filter])
    return query

def apply_fcl_freight_rate_validity_start_less_than_equal_to_filter(query, filters):
    validity_start_less_than_equal_to = filters["fcl_freight_rate"]["validity_start_less_than_equal_to"]
    query = query.where(
        Case(
            None,
            (
                (FclFreightRateAudit.data.contains('%/%/%'), fn.to_date(FclFreightRateAudit.data['validity_start'], 'DD/MM/YY')),
                (FclFreightRateAudit.data.contains('%-%-____'), fn.to_date(FclFreightRateAudit.data['validity_start'], 'DD-MM-YYYY')),
            ),
            fn.to_date(FclFreightRateAudit.data['validity_start'], 'YYYY-MM-DD')
        ) <= fn.to_date(validity_start_less_than_equal_to, 'YYYY-MM-DD')
    )
    return query


def apply_fcl_freight_rate_validity_end_greater_than_equal_to_filter(query, filters):
    validity_start_greater_than_equal_to = filters["fcl_freight_rate"]["validity_start_greater_than_equal_to"]
    query = query.where(
        Case(
            None,
            (
                (FclFreightRateAudit.data.contains('%/%/%'), fn.to_date(FclFreightRateAudit.data['validity_start'], 'DD/MM/YY')),
                (FclFreightRateAudit.data.contains('%-%-____'), fn.to_date(FclFreightRateAudit.data['validity_start'], 'DD-MM-YYYY')),
            ),
            fn.to_date(FclFreightRateAudit.data['validity_start'], 'YYYY-MM-DD')
        ) >= fn.to_date(validity_start_greater_than_equal_to, 'YYYY-MM-DD')
    )
    return query


def apply_fcl_freight_rate_seasonal_surcharge_validity_start_less_than_equal_to_filter(query, filters):
    query = query.where(FclFreightRateSeasonalSurcharge.validity_start <= filters['fcl_freight_rate_seasonal_surcharge']['validity_start_less_than_equal_to'])
    return query

def apply_fcl_freight_rate_seasonal_surcharge_validity_end_greater_than_equal_to_filter(query, filters):
    query = query.where(FclFreightRateSeasonalSurcharge.validity_end >= filters['fcl_freight_rate_seasonal_surcharge']['validity_end_greater_than_equal_to'])
    return query