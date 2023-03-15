from services.fcl_freight_rate.models.fcl_freight_rate_extension_rule_set import FclFreightRateExtensionRuleSets
from operator import attrgetter
from services.fcl_freight_rate.models.fcl_freight_rate import *
from rails_client import client
import peewee
from math import ceil
from playhouse.shortcuts import model_to_dict

POSSIBLE_DIRECT_FILTERS = ['id', 'extension_name', 'service_provider_id', 'shipping_line_id', 'cluster_id', 'cluster_type', 'cluster_reference_name', 'status', 'trade_type']

POSSIBLE_INDIRECT_FILTERS = ['q']

def list_fcl_freight_rate_extension_rule_set_data(request):
    request = request.__dict__
    #request['filters'] = json.loads(request['filters'])
    query = get_query(request)
    query = apply_direct_filters(query, request)
    query = apply_indirect_filters(query, request)
    data = get_data(query)
    # print('Query========',query)
    pagination_data = get_pagination_data(query,request)
    data = {'list':data} | (pagination_data)
    return data


def get_query(request):
    query = (FclFreightRateExtensionRuleSets
        .select()
        .paginate(request['page'], request['page_limit'])
        .order_by(peewee.SQL("t1.{} {}".format(request['sort_by'], request['sort_type'])))
        .from_(FclFreightRateExtensionRuleSets.alias('t1')))
    return query

def apply_direct_filters(query, request):
    for key in request['filters']:
        if key in POSSIBLE_DIRECT_FILTERS:
            query = query.select().where(attrgetter(key)(FclFreightRate) == request['filters'][key]).execute()
    return query

def apply_indirect_filters(query, request):
    for key in request['filters']:
        if key in POSSIBLE_INDIRECT_FILTERS:
            apply_filter_function = f'apply_{key}_filter'      
            query = eval(f'{apply_filter_function}(query, filters)')
    return query

def get_data(query):
    # print('Query========',query)
    results = [model_to_dict(item) for item in query.execute()]
    data = add_service_objects(results)
    return data

def add_service_objects(data):
    unique_cluster_ids = list(set([str(d['cluster_id']) for d in data]))
    unique_shipping_line_ids = list(set([str(d['shipping_line_id']) for d in data]))
    unique_service_provider_ids = list(set([str(d['service_provider_id']) for d in data]))
    params = {'objects' : [
      {
        'name': 'location_cluster',
        'filters': {'id': unique_cluster_ids},
        'fields': ['id', 'cluster_name', 'cluster_type', 'location_type']
      },
      {
        'name': 'fcl_freight_commodity_cluster',
        'filters': {'id': unique_cluster_ids},
        'fields': ['id', 'name']
      },
      {
        'name': 'operator',
        'filters': { 'id': unique_shipping_line_ids },
        'fields': ['id', 'business_name', 'short_name', 'logo_url']
      },
      {
        'name': 'organization',
        'filters': { 'id': unique_service_provider_ids },
        'fields': ['id', 'business_name', 'short_name']
      }
    ]}
    service_objects = client.ruby.get_multiple_service_objects_data_for_fcl(params)
    new_data = []
    for object in data:
        object['location_cluster'] = service_objects['location_cluster'][object['cluster_id']] if 'location_cluster' in service_objects and object.get('cluster_id') in service_objects['location_cluster'] else None
        try:
            object['fcl_freight_commodity_cluster'] = service_objects['fcl_freight_commodity_cluster'][object['cluster_id']]
        except:
            object['fcl_freight_commodity_cluster'] = None
        try:
            object['shipping_line'] = service_objects['operator'][object['shipping_line_id']]
        except:
            object['shipping_line'] = None
        try:
            object['service_provider'] = service_objects['organization'][object['service_provider_id']]
        except:
            object['service_provider'] = None
        new_data.append(object)
    
    return new_data

def get_pagination_data(query,request):
    return {
        'page': request['page'],
        'total': ceil(query.count()/request['page_limit']),
        'total_count': query.count(),
        'page_limit': request['page_limit']
    }