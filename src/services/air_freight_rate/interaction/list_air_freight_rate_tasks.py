from fastapi import HTTPException
from datetime import datetime
from libs.get_filters import get_filters
from services.air_freight_rate.models.air_freight_rate_tasks import AirFreightRateTasks
from configs.air_freight_rate_constants import EXPECTED_TAT
from libs.json_encoder import json_encoder

POSSIBLE_DIRECT_FILTERS = ['airport_id', 'logistics_service_type', 'commodity', 'airline_id', 'trade_type', 'status', 'task_type']
POSSIBLE_INDIRECT_FILTERS = ['updated_at_greater_than', 'updated_at_less_than']

def list_air_freight_rate_tasks(filters={},page_limit=10,page=1,sort_by = 'created_at', sort_type = 'desc', stats_required = True, pagination_data_required = True):
    query = get_query(sort_by, sort_type)
    filters = {k for k,v  in filters.items() if v is not None}
    unexpected_filters = set(filters.keys()) - (set(POSSIBLE_DIRECT_FILTERS) | set(POSSIBLE_INDIRECT_FILTERS))
    filters = {k for k in filters.items() if k not in unexpected_filters}

    query=get_filters(POSSIBLE_DIRECT_FILTERS,query,AirFreightRateTasks)
    query=apply_indirect_filters(query,filters)

    pagination_data=get_pagination_data(query,page,page_limit)
    query=query.paginate(page,page_limit)
    data=get_data(query,filters)

    stats=get_stats(filters)

    return{
        'list':json_encoder(data)
    } | (pagination_data) |(stats)

def apply_indirect_filters(query, filters):
    for key in filters:
        if key in POSSIBLE_INDIRECT_FILTERS:
            apply_filter_function = f'apply_{key}_filter'
            query = eval(f'{apply_filter_function}(query, filters)')
    return query 
def get_pagination_data(query,page,page_limit):
    return 

def get_data(query,filters):
    return 
def get_stats(filters):
    return 
def get_query(sort_type,sort_by):
    return 