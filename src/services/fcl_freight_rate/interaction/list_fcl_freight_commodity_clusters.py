from services.fcl_freight_rate.models.fcl_freight_commodity_cluster import FclFreightCommodityCluster
from services.fcl_freight_rate.helpers.find_or_initialize import apply_direct_filters
from math import ceil
from playhouse.shortcuts import model_to_dict
from peewee import fn
import json

possible_direct_filters = ['id', 'status']
possible_indirect_filters = ['q']

def list_fcl_freight_commodity_clusters(filters = {}, page_limit = 10, page = 1, pagination_data_required = True, sort_by = 'updated_at', sort_type = 'desc'):
    query = get_query(sort_by, sort_type, page, page_limit)
    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)
        query = apply_direct_filters(query, filters, possible_direct_filters, FclFreightCommodityCluster)
        query = apply_indirect_filters(query, filters)

    data = [model_to_dict(item) for item in query.execute()]
    pagination_data = get_pagination_data(query, page, page_limit, pagination_data_required)

    return {'list': data } | (pagination_data)
    
def get_query(sort_by, sort_type, page, page_limit):
    query = FclFreightCommodityCluster.select().order_by(eval("FclFreightCommodityCluster.{}.{}()".format(sort_by, sort_type))).paginate(page, page_limit)
    return query

def apply_indirect_filters(query, filters):
    for key in filters:
        if key in possible_indirect_filters:
            apply_filter_function = f'apply_{key}_filter'
            query = eval(f'{apply_filter_function}(query, filters)')
    return query

def apply_q_filter(query, filters):
    query = query.where(fn.Lower(FclFreightCommodityCluster.name).contains(filters['q'].lower()))
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