from operator import attrgetter
from services.fcl_freight_rate.models.fcl_freight_rate_bulk_operation import FclFreightRateBulkOperation
from math import ceil 
from playhouse.shortcuts import model_to_dict

possible_direct_filters = ['action_name', 'service_provider_id']
possible_indirect_filters = []

def list_fcl_freight_rate_bulk_operations(filters, page, page_limit):
    query = get_query(page, page_limit)
    query = apply_direct_filters(query, filters)
    query = apply_indirect_filters(query, filters)

    data = get_data(query)
    pagination_data = get_pagination_data(query, page, page_limit)

    return {'list': data } | (pagination_data)

def get_query(page, page_limit):
    query = FclFreightRateBulkOperation.select().order_by(FclFreightRateBulkOperation.updated_at.desc()).paginate(page, page_limit)
    return query

def get_data(query):
    data = [model_to_dict(item) for item in query.execute()]
    return data 

def get_pagination_data(query, page, page_limit):
    params = {
      'page': page,
      'total': ceil(query.count()/page_limit),
      'total_count': query.count(),
      'page_limit': page_limit
    }
    return {'get_pagination_data':params}
  
def apply_direct_filters(query, filters):
    for key in filters:
        if key in possible_direct_filters:
            query = query.select().where(attrgetter(key)(FclFreightRateBulkOperation) == filters[key])
    return query

def apply_indirect_filters(query, filters):
    for key in filters:
        if key in possible_indirect_filters:
            apply_filter_function = f'apply_{key}_filter'
            query = eval(f'{apply_filter_function}(query, filters)')
    return query