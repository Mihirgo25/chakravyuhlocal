from services.ftl_freight_rate.models.truck import Truck
from fastapi.encoders import jsonable_encoder
from math import ceil
import json
from libs.get_filters import get_filters
from libs.get_applicable_filters import get_applicable_filters

# define filters
possible_direct_filters = ['id','truck_company','truck_name','created_at','mileage','mileage_unit','capacity','capacity_unit','vehicle_weight','vehicle_weight_unit','fuel_type','avg_speed','no_of_wheels','engine_type','country_id','axels','truck_type','body_type','status','horse_power','updated_at','display_name']
possible_indirect_filters = ['q','capacity_greater_equal_than']

def list_trucks_data(filters, page_limit, page, sort_by, sort_type):
    # make sql query
    query = get_query(sort_by, sort_type, page, page_limit)

    # use filters and filter out required data
    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)

        # get applicable filters
        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)
        # direct filters
        query = get_filters(direct_filters, query, Truck)
        # indirect filters
        query = apply_indirect_filters(query, indirect_filters)

    # # apply pagination
    # pagination_data = get_pagination_data(query, page, page_limit)

    data = jsonable_encoder(list(query.dicts()))

    return {'list': data }

# sql query
def get_query(sort_by, sort_type, page, page_limit):
    query = Truck.select().order_by(eval("Truck.{}.{}()".format(sort_by, sort_type))).paginate(page, page_limit)
    return query

# # split data into pages
# def get_pagination_data(query, page, page_limit, pagination_data_required):
#     if not pagination_data_required:
#         return {}

#     total_count = query.count()
#     params = {
#       'page': page,
#       'total': ceil(total_count/page_limit),
#       'total_count': total_count,
#       'page_limit': page_limit
#     }
#     return params

# indirect filters
def apply_indirect_filters(query, filters):
    for key in filters:
        if key in possible_indirect_filters:
            apply_filter_function = f'apply_{key}_filter'
            query = eval(f'{apply_filter_function}(query, filters)')
    return query

# ILIKE filter to search in truck display name
def apply_q_filter(query, filters):
    return query.where(Truck.display_name.contains(filters['q']))

# filter greater than or equal to capacity
def apply_capacity_greater_equal_than_filter(query, filters):
    return query.where(Truck.capacity >= filters['capacity_greater_equal_than'])
