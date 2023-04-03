from services.fcl_freight_rate.models.fcl_freight_rate_extension_rule_set import FclFreightRateExtensionRuleSet
from services.fcl_freight_rate.models.fcl_freight_rate import *
import peewee, json
from math import ceil
from micro_services.client import maps
from libs.get_filters import get_filters
from libs.get_applicable_filters import get_applicable_filters
from services.fcl_freight_rate.interaction.list_fcl_freight_commodity_clusters import list_fcl_freight_commodity_clusters

possible_direct_filters = ['id', 'extension_name', 'service_provider_id', 'shipping_line_id', 'cluster_id', 'cluster_type', 'cluster_reference_name', 'status', 'trade_type']

possible_indirect_filters = ['q']

def list_fcl_freight_rate_extension_rule_set_data(filters = {}, page_limit = 10, page = 1, sort_by = 'updated_at', sort_type = 'desc'):
    query = get_query(sort_by, sort_type)
    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)
        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)
  
        query = get_filters(direct_filters, query, FclFreightRateExtensionRuleSet)
        query = apply_indirect_filters(query, indirect_filters)

    pagination_data = get_pagination_data(query, page, page_limit)
    query = query.paginate(page, page_limit)
    data = get_data(query)

    data = {'list':data} | (pagination_data)
    return data


def get_query(sort_by, sort_type):
    query = (FclFreightRateExtensionRuleSet
        .select()
        .order_by(peewee.SQL("t1.{} {}".format(sort_by, sort_type)))
        .from_(FclFreightRateExtensionRuleSet.alias('t1')))
    return query


def apply_indirect_filters(query, filters):
    for key in filters:
        if key in possible_indirect_filters:
            apply_filter_function = f'apply_{key}_filter'      
            query = eval(f'{apply_filter_function}(query, filters)')
    return query


def apply_q_filter(query, filters):
    return query.where(FclFreightRateExtensionRuleSet.extension_name.contains(filters['q']))

def get_data(query):
    data = [x for x in query.dicts()]
    param = {'id':[x['cluster_id'] for x in data]}
    cluster_data_all = maps.list_location_cluster({'filters': param})['list']
    commodity_cluster_data_all = list_fcl_freight_commodity_clusters(filters = param)['list']
    cluster_dict={}
    commodity_cluster_dict ={}
    for cluster in cluster_data_all:
        cluster_dict[str(cluster['id'])] = {'id':cluster['id'], 'cluster_name' : cluster['cluster_name'], 'cluster_type':cluster['cluster_type'], 'location_type':cluster['location_type']}
    for commodity_cluster in commodity_cluster_data_all:
        commodity_cluster_dict[str(commodity_cluster['id'])]={'id':commodity_cluster['id'], 'name' : commodity_cluster['name']}
        
    for each in range(0,len(data)):
        if cluster_dict.get(str(data[each]['cluster_id'])):
            data[each]['location_cluster'] = cluster_dict[str(data[each]['cluster_id'])]
        else:
            data[each]['location_cluster'] = {}
        if commodity_cluster_dict.get(str(data[each]['cluster_id'])):
            data[each]['fcl_freight_commodity_cluster'] = commodity_cluster_dict[str(data[each]['cluster_id'])]
        else:
            data[each]['fcl_freight_commodity_cluster'] = {}
    return data
        
def get_pagination_data(query, page, page_limit):
    total_count = query.count()
    return {
        'page': page,
        'total': ceil(total_count/page_limit),
        'total_count': total_count,
        'page_limit': page_limit
    }