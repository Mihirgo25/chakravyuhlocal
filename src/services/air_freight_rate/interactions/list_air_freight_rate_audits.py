from services.air_freight_rate.models.air_freight_rate_audit import AirFreightRateAudit
from libs.get_applicable_filters import get_applicable_filters
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from libs.get_filters import get_filters
from libs.json_encoder import json_encoder
import json
from math import ceil
from peewee import *

POSSIBLE_HASH_FILTERS ={ 'air_freight_rate':{'direct':['origin_airport_id', 'destination_airport_id', 'commodity', 'airline_id', 'operation_type', 'service_provider_id']}}
POSSIBLE_INDIRECT_FILTERS = []
POSSIBLE_DIRECT_FILTERS = []
def list_air_freight_rate_audits(filters={},page_limit=10,page=1,sort_by = 'created_at', sort_type = 'desc', stats_required = True, pagination_data_required = True):
    query = get_query(sort_by, sort_type)
    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)
        direct_filters, indirect_filters = get_applicable_filters(filters, POSSIBLE_DIRECT_FILTERS, POSSIBLE_INDIRECT_FILTERS)
    
        query = get_filters(direct_filters, query, AirFreightRateAudit)
        query = apply_indirect_filters(query, indirect_filters)
        query = apply_hash_filters(query,filters)
    pagination_data=get_pagination_data(query,page,page_limit)

    query=query.paginate(page,page_limit)
    data=get_data(query)
    return{
        'list':json_encoder(data)
    } | (pagination_data)

def get_query(sort_by, sort_type):
    query = AirFreightRateAudit.select().order_by(eval("AirFreightRateAudit.{}.{}()".format(sort_by,sort_type)))
    return query

def apply_indirect_filters(query, filters):
    for key in filters:
        if key in POSSIBLE_INDIRECT_FILTERS:
            apply_filter_function = f'apply_{key}_filter'
            query = eval(f'{apply_filter_function}(query, filters)')
    return query 

def get_pagination_data(query,page,page_limit):
    total_count=query.count()
    params={
      'page': page,
      'total': ceil(total_count/page_limit),
      'total_count': total_count,
      'page_limit': page_limit

    }
    return params

def apply_hash_filters(query,filters):
    possible_hash_filters = {key:value for key,value in filters.items() if key in POSSIBLE_HASH_FILTERS.keys()}
    hash_filters = possible_hash_filters.keys()
    for hash_filter in hash_filters:
        query = eval("apply_{}_filter(query, filters)".format(filter))
        if 'direct' in possible_hash_filters[hash_filter].keys():
            direct_filters = possible_hash_filters[hash_filters]['direct']
            for key,value in direct_filters.items():
                query = eval("apply_hash_direct_filter(query,{},{})".format(key,value))
    return query
                
def apply_air_freight_rate_filter(query, filters):
    query = query.select().join(AirFreightRate, JOIN.INNER, on=(AirFreightRateAudit.object_id == AirFreightRate.id)).where(AirFreightRateAudit.object_type == 'AirFreightRate')
    return query

def apply_hash_direct_filter(query,key,value):
    query = query.select().where(
        eval("AirFreightRate.{}".format(key)==value)
    )

def get_data(query):
    data = json_encoder(query.dicts())
    return data
    

