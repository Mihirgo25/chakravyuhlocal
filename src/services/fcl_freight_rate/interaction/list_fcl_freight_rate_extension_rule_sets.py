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
    location_cluster_ids = []
    commodity_cluster_ids = []
    for val in data:
        if val['cluster_type'] == 'location':
            location_cluster_ids.append(val['cluster_id'])
        elif val['cluster_type'] == 'commodity':
            commodity_cluster_ids.append(val['cluster_id'])

    all_location_clusters = maps.list_location_cluster({'filters': {'id': list(set(location_cluster_ids))}})['list']
    location_clusters = {}
    for val in all_location_clusters:
        location_clusters[str(val['id'])] = {
            'id': str(val['id']),
            'cluster_name': val['cluster_name'],
            'cluster_type': val['cluster_type'],
            'location_type': val['location_type']
        }

    all_commodity_clusters = list_fcl_freight_commodity_clusters(filters = {'id': list(set(commodity_cluster_ids))})['list']
    commodity_clusters = {}
    for val in all_commodity_clusters:
        commodity_clusters[str(val['id'])] = {
            'id': str(val['id']),
            'name': val['name']
        }

    for object in data:
        object['location_cluster'] = location_clusters.get(str(object['cluster_id']), {})
        object['fcl_freight_commodity_cluster'] = commodity_clusters.get(str(object['cluster_id']), {})

    return data

def get_pagination_data(query, page, page_limit):
    total_count = query.count()
    return {
        'page': page,
        'total': ceil(total_count/page_limit),
        'total_count': total_count,
        'page_limit': page_limit
    }
