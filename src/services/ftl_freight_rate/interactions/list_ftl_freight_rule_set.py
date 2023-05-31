from services.ftl_freight_rate.models.ftl_freight_rate_rule_set import FtlFreightRateRuleSet
from fastapi.encoders import jsonable_encoder
from math import ceil
import json
from libs.get_filters import get_filters
from libs.get_applicable_filters import get_applicable_filters

possible_direct_filters = ['id','location_id','location_type','truck_type','process_type','process_unit','process_value','process_currency','status','created_at','updated_at']
possible_indirect_filters = []

def list_ftl_rule_set_data(filters, page_limit, page, sort_by, sort_type, pagination_data_required):
    # make sql query
    query = get_query(sort_by, sort_type)

    # use filters and filter out required data
    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)

        # get applicable filters
        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)
        # direct filters
        query = get_filters(direct_filters, query, FtlFreightRateRuleSet)
        # indirect filters
        query = apply_indirect_filters(query, indirect_filters)

    # apply pagination

    query, total_count = apply_pagination(query, page, page_limit)

    pagination_data = get_pagination_data(query, page, page_limit, pagination_data_required, total_count)

    data = jsonable_encoder(list(query.dicts()))

    return {'list': data } | (pagination_data)

# sql query
def get_query(sort_by, sort_type):
    query = FtlFreightRateRuleSet.select().order_by(eval("FtlFreightRateRuleSet.{}.{}()".format(sort_by, sort_type)))
    return query

def apply_pagination(query, page, page_limit):
    offset = (page - 1) * page_limit
    total_count = query.count()
    query = query.offset(offset).limit(page_limit)
    return query, total_count

# split data into pages
def get_pagination_data(query, page, page_limit, pagination_data_required, total_count):
    if not pagination_data_required:
        return {}

    params = {
      'page': page,
      'total': ceil(total_count/page_limit),
      'total_count': total_count,
      'page_limit': page_limit
    }
    return params

# indirect filters
def apply_indirect_filters(query, filters):
    for key in filters:
        if key in possible_indirect_filters:
            apply_filter_function = f'apply_{key}_filter'
            query = eval(f'{apply_filter_function}(query, filters)')
    return query
