from fastapi import HTTPException
from datetime import datetime ,timedelta
from services.air_freight_rate.models.air_freight_storage_rate import AirFreightStorageRates
from services.fcl_freight_rate.helpers.direct_filters import apply_direct_filters
from libs.json_encoder import json_encoder
from libs.get_applicable_filters import get_applicable_filters
from libs.get_filters import get_filters
import json

POSSIBLE_DIRECT_FILTERS = ['id', 'airport_id', 'country_id', 'trade_id', 'continent_id', 'trade_type', 'commodity', 'airline_id','service_provider_id','priority_score', 'free_limit', 'is_slabs_missing']

POSSIBLE_INDIRECT_FILTERS=['location_ids']

def list_air_freight_storage_rates(filters={},page=1,page_limit=10,pagination_data_required=True,return_query=False):
    query=get_query()

    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)

        direct_filters, indirect_filters = get_applicable_filters(filters, POSSIBLE_DIRECT_FILTERS, POSSIBLE_INDIRECT_FILTERS)
    
        query = get_filters(direct_filters, query, AirFreightStorageRates)
        query = apply_indirect_filters(query, indirect_filters)

    
    if return_query:
        query=query.paginate(page,page_limit)
        return {
            'list':json_encoder(list(query.dicts()))
    }
    pagination_data={}
    if pagination_data_required:
        pagination_data=get_pagination_data(query)
    query=query.paginate(page,page_limit)

    return { 'list': json_encoder(list(query.dicts())) } | (pagination_data)

def apply_indirect_filters(query, filters):
    for key in filters:
        if key in POSSIBLE_INDIRECT_FILTERS:
            apply_filter_function = f'apply_{key}_filter'
            query = eval(f'{apply_filter_function}(query, filters)')
    return query

def apply_location_ids_filter(query,filters):
    locations_ids = filters['location_ids']
    return query.where(AirFreightStorageRates.location_ids.contains(locations_ids))


def get_query():
    query=AirFreightStorageRates.select( 
        AirFreightStorageRates.airport_id,
        AirFreightStorageRates.trade_type,
        AirFreightStorageRates.commodity,
        AirFreightStorageRates.airline_id,
        AirFreightStorageRates.service_provider_id,
        AirFreightStorageRates.free_limit,
        AirFreightStorageRates.remarks,
        AirFreightStorageRates.slabs,
        AirFreightStorageRates.is_slabs_missing).order_by(AirFreightStorageRates.updated_at.desc())
    return query


def get_pagination_data(query, page, page_limit):
    total_count = query.count()
    params = {
      'page': page,
      'total': ceil(total_count/page_limit),
      'total_count': total_count,
      'page_limit': page_limit
    }
    return params







