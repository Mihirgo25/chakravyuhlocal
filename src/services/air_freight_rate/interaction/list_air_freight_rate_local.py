from services.air_freight_rate.models.air_freight_rate_local import AirFreightRateLocal
from fastapi.encoders import jsonable_encoder

possible_direct_filters = ['id', 'airport_id', 'country_id', 'trade_id', 'continent_id', 'trade_type', 'commodity', 'airline_id', 'service_provider_id', 'is_line_items_info_messages_present', 'is_line_items_error_messages_present', 'rate_type']

possible_indirect_filters = ['location_ids']

def list_air_freight_rate_locals(filters={},page_limit=10,page=1,sort_by='update_at',sort_type='desc',return_query=False):
    query=get_query(sort_by,sort_type,page,page_limit)
    
    # query=apply_direct_filters(query)
    query=apply_indirect_filters(query,filters)

    # data=get_data(query)
    pagination_data=get_pagination_data(query)

def get_query(sort_by,sort_type,page,page_limit):
    
    query=AirFreightRateLocal.select(
            AirFreightRateLocal.id,
            AirFreightRateLocal.airport_id,
            AirFreightRateLocal.country_id,
            AirFreightRateLocal.trade_id,
            AirFreightRateLocal.continent_id,
            AirFreightRateLocal.trade_type,
            AirFreightRateLocal.commodity,
            AirFreightRateLocal.airline_id,
            AirFreightRateLocal.service_provider_id,
            AirFreightRateLocal.is_line_items_info_messages_present,
            AirFreightRateLocal.rate_type,
            

        ).order_by(eval('AirFreightRateLocal.{}.{}'.format(sort_by,sort_type))).paginate(page,page_limit)
    return query

# def get_data(query):
#     data=[]

#     all_list=jsonable_encoder(list(query.dicts()))

#     for result in all_list:




# def apply_direct_filters(query):
#     direct_filters=

def apply_indirect_filters(query,filters):
    
    for key in filters:
        if key in possible_indirect_filters:
            apply_filter_function = f'apply_{key}_filter'
            query = eval(f'{apply_filter_function}(query, filters)')
    return query

def get_pagination_data(query):
    print(query.total_pages)
    return {
        "page": query.page,
        "total": query.total_pages,
        "total_count": query.total_count,
        "page_limit": query.page_limit
    }