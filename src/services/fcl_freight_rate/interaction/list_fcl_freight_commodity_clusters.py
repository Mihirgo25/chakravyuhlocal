from services.fcl_freight_rate.models.fcl_freight_commodity_cluster import FclFreightCommodityCluster
from operator import attrgetter
from math import ceil
from playhouse.shortcuts import model_to_dict
from peewee import fn
from services.fcl_freight_rate.interaction.list_fcl_freight_rates import remove_unexpected_filters

possible_direct_filters = ['id', 'status']
possible_indirect_filters = ['q']

def list_fcl_freight_commodity_clusters(filters, page, page_limit, pagination_data_required, sort_by, sort_type):
    filters = remove_unexpected_filters(filters)
    query = get_query(sort_by, sort_type, page, page_limit)
    query = apply_direct_filters(query, filters)
    query = apply_indirect_filters(query, filters)

    data = [model_to_dict(item) for item in query.execute()]
    pagination_data = get_pagination_data(query, page, page_limit, pagination_data_required)
    return {'list': data } | (pagination_data)

def get_query(sort_by, sort_type, page, page_limit):
    query = FclFreightCommodityCluster.select().order_by(eval("FclFreightCommodityCluster.{}.{}()".format(sort_by, sort_type)).paginate(page, page_limit))
    return query

def apply_direct_filters(query, filters):
    for key in filters:
        if key in possible_direct_filters:
            query = query.select().where(attrgetter(key)(FclFreightCommodityCluster) == filters[key])
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
    if pagination_data_required:
        return {} 

    params = {
      'page': page,
      'total': ceil(query.count()/page_limit),
      'total_count': query.count(),
      'page_limit': page_limit
    }
    return params