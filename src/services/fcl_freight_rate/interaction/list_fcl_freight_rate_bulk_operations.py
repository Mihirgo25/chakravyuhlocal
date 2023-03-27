from services.fcl_freight_rate.helpers.direct_filters import apply_direct_filters
from services.fcl_freight_rate.models.fcl_freight_rate_bulk_operation import FclFreightRateBulkOperation
from math import ceil 
from playhouse.shortcuts import model_to_dict
import json

possible_direct_filters = ['action_name', 'service_provider_id']
possible_indirect_filters = []

def list_fcl_freight_rate_bulk_operations(filters = {}, page_limit = 10, page = 1):
    query = get_query(page, page_limit)

    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)

        query = apply_direct_filters(query, filters, possible_direct_filters, FclFreightRateBulkOperation)

    data = [model_to_dict(item) for item in query.execute()]
    pagination_data = get_pagination_data(data, page, page_limit)

    return {'list': data } | (pagination_data)

def get_query(page, page_limit):
    query = FclFreightRateBulkOperation.select().order_by(FclFreightRateBulkOperation.updated_at.desc()).paginate(page, page_limit)
    return query

def get_pagination_data(data, page, page_limit):
    params = {
      'page': page,
      'total': ceil(len(data)/page_limit),
      'total_count': len(data),
      'page_limit': page_limit
    }
    return params

def apply_indirect_filters(query, filters):
    for key in filters:
        if key in possible_indirect_filters:
            apply_filter_function = f'apply_{key}_filter'
            query = eval(f'{apply_filter_function}(query, filters)')
    return query