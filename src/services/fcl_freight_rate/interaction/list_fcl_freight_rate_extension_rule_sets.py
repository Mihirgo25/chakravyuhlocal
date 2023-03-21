from services.fcl_freight_rate.models.fcl_freight_rate_extension_rule_set import FclFreightRateExtensionRuleSets
from services.fcl_freight_rate.models.fcl_freight_rate import *
from services.fcl_freight_rate.helpers.find_or_initialize import apply_direct_filters
import peewee, json
from math import ceil
from micro_services.client import maps
from services.fcl_freight_rate.interaction.list_fcl_freight_commodity_clusters import list_fcl_freight_commodity_clusters

possible_direct_filters = ['id', 'extension_name', 'service_provider_id', 'shipping_line_id', 'cluster_id', 'cluster_type', 'cluster_reference_name', 'status', 'trade_type']

possible_indirect_filters = ['q']

def list_fcl_freight_rate_extension_rule_set_data(filters = {}, page_limit = 10, page = 1, sort_by = 'updated_at', sort_type = 'desc'):
    query = get_query(page, page_limit, sort_by, sort_type)
    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)

        query = apply_direct_filters(query, filters, possible_direct_filters, FclFreightRateExtensionRuleSets)
        query = apply_indirect_filters(query, filters)

    data = get_data(query)
    pagination_data = get_pagination_data(query, page, page_limit)

    data = {'list':data} | (pagination_data)
    return data


def get_query(page, page_limit, sort_by, sort_type):
    query = (FclFreightRateExtensionRuleSets
        .select()
        .paginate(page, page_limit)
        .order_by(peewee.SQL("t1.{} {}".format(sort_by, sort_type)))
        .from_(FclFreightRateExtensionRuleSets.alias('t1')))
    return query


def apply_indirect_filters(query, filters):
    for key in filters:
        if key in possible_indirect_filters:
            apply_filter_function = f'apply_{key}_filter'      
            query = eval(f'{apply_filter_function}(query, filters)')
    return query


def apply_q_filter(query, filters):
    return query.where(FclFreightRateExtensionRuleSets.extension_name.contains(filters['q']))

def get_data(query):
    data = []
    for item in query.dicts():
        cluster_data = maps.list_location_cluster({'filters':{'id':item['cluster_id']}})
        if cluster_data['list']:
            item['location_cluster'] = {'id':cluster_data['list'][0]['id'], 'cluster_name' : cluster_data['list'][0]['cluster_name'], 'cluster_type':cluster_data['list'][0]['cluster_type'], 'location_type':cluster_data['list'][0]['location_type']}
        else:
            item['location_cluster'] = {}
        commodity_cluster_data = list_fcl_freight_commodity_clusters(filters = {'id':item['cluster_id']})
        if commodity_cluster_data['list']:
            item['fcl_freight_commodity_cluster'] = {'id':commodity_cluster_data['list'][0]['id'], 'name' : commodity_cluster_data['list'][0]['name']}
        else:
            item['fcl_freight_commodity_cluster'] = {}
        data.append(item)
    return data
        
def get_pagination_data(query, page, page_limit):
    return {
        'page': page,
        'total': ceil(query.count()/page_limit),
        'total_count': query.count(),
        'page_limit': page_limit
    }