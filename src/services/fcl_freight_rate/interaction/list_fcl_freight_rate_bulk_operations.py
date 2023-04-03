from services.fcl_freight_rate.helpers.direct_filters import apply_direct_filters
from services.fcl_freight_rate.models.fcl_freight_rate_bulk_operation import FclFreightRateBulkOperation
from math import ceil 
from fastapi.encoders import jsonable_encoder
from libs.get_filters import get_filters
from libs.get_applicable_filters import get_applicable_filters
import json

possible_direct_filters = ['action_name', 'service_provider_id']
possible_indirect_filters = []

def list_fcl_freight_rate_bulk_operations(filters = {}, page_limit = 10, page = 1):
    query = FclFreightRateBulkOperation.select().order_by(FclFreightRateBulkOperation.updated_at.desc())

    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)

        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)
  
        query = get_filters(direct_filters, query, FclFreightRateBulkOperation)

    pagination_data = get_pagination_data(query, page, page_limit)
    query = query.paginate(page, page_limit)
    data = jsonable_encoder(list(query.dicts()))

    return {'list': data } | (pagination_data)

def get_pagination_data(query, page, page_limit):
    total_count = query.count()
    params = {
      'page': page,
      'total': ceil(total_count/page_limit),
      'total_count': total_count,
      'page_limit': page_limit
    }
    return params

def apply_indirect_filters(query, filters):
    for key in filters:
        if key in possible_indirect_filters:
            apply_filter_function = f'apply_{key}_filter'
            query = eval(f'{apply_filter_function}(query, filters)')
    return query