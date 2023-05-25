from playhouse.postgres_ext import *
from peewee import *

from services.ftl_freight_rate.models.truck import Truck
from fastapi.encoders import jsonable_encoder
from math import ceil
import json
from libs.get_filters import get_filters
from libs.get_applicable_filters import get_applicable_filters


# define filters
POSSIBLE_DIRECT_FILTERS = ['id','truck_company','truck_name','created_at','mileage','mileage_unit','capacity','capacity_unit','vehicle_weight','vehicle_weight_unit','fuel_type','avg_speed','no_of_wheels','engine_type','country_id','axels','truck_type','body_type','status','horse_power','updated_at','display_name']
POSSIBLE_INDIRECT_FILTERS = ['q','capacity_greater_equal_than', 'vehicle_weight_greater_equal_than']
TS_MATCH = "@@"
TS_FULL_MATCH = "<->"

def list_trucks_data(filters, page_limit, page, sort_by, sort_type, pagination_data_required):
    # make sql query
    query = get_query(sort_by, sort_type)

    # use filters and filter out required data
    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)

        # get applicable filters
        direct_filters, indirect_filters = get_applicable_filters(filters, POSSIBLE_DIRECT_FILTERS, POSSIBLE_INDIRECT_FILTERS)
        # direct filters
        query = get_filters(direct_filters, query, Truck)
        # indirect filters
        query = apply_indirect_filters(query, indirect_filters)

    query, total_count = apply_pagination(query, page, page_limit)

    # apply pagination
    pagination_data = get_pagination_data(query, page, page_limit, pagination_data_required, total_count)

    data = jsonable_encoder(list(query.dicts()))

    return {'list': data } | (pagination_data)

# sql query
def get_query(sort_by, sort_type):
    query = Truck.select().order_by(eval("Truck.{}.{}()".format(sort_by, sort_type)))
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
    for key, val in filters.items():
        if key in POSSIBLE_INDIRECT_FILTERS:
            apply_filter_function = f'apply_{key}_filter'
            query = eval(f'{apply_filter_function}(query, val)')
    return query

def set_and_constraints(val):
    val = val.strip()
    fields = val.split(" ")
    for itr in range(len(fields) - 1):
        if len(fields[itr]) != 0:
            fields[itr] = fields[itr] + ":&"
    if len(fields[-1]) != 0:
        fields[-1] = fields[-1] + ":*"
    fields = "".join(fields)
    return fields

def Match(field, query, language=None):
    params = (language, query) if language is not None else (query,)
    field_params = (language, field) if language is not None else (field,)
    params = fn.to_tsquery(*params)
    return Expression(field_params,TS_MATCH,params)

def set_or_constraints(val):
    val = val.strip()
    fields = val.split(" ")
    for itr in range(len(fields) - 1):
        if len(fields[itr]) != 0:
            fields[itr] = fields[itr] + "|"
    if len(fields[-1]) != 0:
        fields[-1] = fields[-1] + ":*"
    fields = "".join(fields)
    return fields

# Q filter
def apply_q_filter(query, val):
    val = val.translate ({ord(c): " " for c in "!@#$%^&*()[]{};:,./<>?\|`~-=_+"})
    if not val:
        return query
    search_field = set_and_constraints(val)
    # print(search_field)
    search_query = query.where(
        Match(Truck.search_vector, search_field)
    )
    if search_query.count() == 0:
        search_field = set_or_constraints(val)
        search_query = query.where(Match(Truck.search_vector, search_field))

        if search_query.count() == 0:
            return query

    query = search_query.order_by(SQL("id desc"))
    return query

# filter greater than or equal to capacity
def apply_capacity_greater_equal_than_filter(query, val):
    return query.where(Truck.capacity >= val)

def apply_vehicle_weight_greater_equal_than_filter(query, val):
    return query.where(Truck.vehicle_weight >= val)
