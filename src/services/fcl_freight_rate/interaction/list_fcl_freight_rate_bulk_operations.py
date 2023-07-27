from services.fcl_freight_rate.helpers.direct_filters import apply_direct_filters
from services.fcl_freight_rate.models.fcl_freight_rate_bulk_operation import FclFreightRateBulkOperation
from math import ceil 
from libs.json_encoder import json_encoder
from libs.get_filters import get_filters
from libs.parse_numeric import parse_numeric
from libs.get_applicable_filters import get_applicable_filters
from services.fcl_freight_rate.helpers.fcl_freight_rate_bulk_operation_helpers import get_progress_percent, get_total_affected_rates
import json

possible_direct_filters = ['action_name', 'service_provider_id', 'performed_by_id', ]
possible_indirect_filters = []

def list_fcl_freight_rate_bulk_operations(filters = {}, page_limit = 10, page = 1, sort_by = 'updated_at', sort_type = 'desc',):
    query = get_query(sort_by, sort_type)

    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)

        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)
  
        query = get_filters(direct_filters, query, FclFreightRateBulkOperation)

    pagination_data = get_pagination_data(query, page, page_limit)
    query = query.paginate(page, page_limit)
    data = json_encoder(list(query.dicts()))
    data = get_details(data)

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

def get_details(data):
    for d in data: 
        progress = parse_numeric(d.get('progress')) or 0
        total_affected_rates = parse_numeric(d['data'].get('total_affected_rates')) or 0
        d['data']['total_affected_rates'] = get_total_affected_rates(str(d['id']), total_affected_rates)
        d['progress'] = 100 if progress == 100 else min(get_progress_percent(str(d['id']), progress), 100)
    return data

def get_query(sort_by, sort_type):
    query = FclFreightRateBulkOperation.select()
    if(sort_by):
        query = query.order_by(eval('FclFreightRateBulkOperation.{}.{}()'.format(sort_by,sort_type)))
        
    return query
    