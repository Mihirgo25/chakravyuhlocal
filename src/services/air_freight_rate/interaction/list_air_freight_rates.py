from datetime import datetime,timedelta
import json
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from libs.get_applicable_filters import get_applicable_filters
from libs.get_filters import get_filters
from math import ceil
from configs.global_constants import SEARCH_START_DATE_OFFSET

POSSIBLE_DIRECT_FILTERS = ['id', 'origin_airport_id', 'origin_country_id', 'origin_trade_id', 'origin_continent_id', 'destination_airport_id', 'destination_country_id', 'destination_trade_id', 'destination_continent_id', 'airline_id', 'commodity', 'operation_type', 'service_provider_id', 'rate_not_available_entry', 'price_type', 'shipment_type', 'stacking_type', 'commodity_type', 'cogo_entity_id', 'rate_type']

POSSIBLE_INDIRECT_FILTERS = ['location_ids', 'is_rate_about_to_expire', 'is_rate_available', 'is_rate_not_available', 'last_rate_available_date_greater_than', 'procured_by_id', 'is_rate_not_available_entry', 'origin_location_ids', 'destination_location_ids', 'density_category', 'partner_id', 'available_volume_range', 'available_gross_weight_range', 'achieved_volume_percentage', 'achieved_gross_weight_percentage', 'updated_at']


def list_air_freight_rate(request):
    request['filters'] = {k for k,v  in request.get('filters').items() if v is not None}
    unexpected_filters = set(request['filters'].keys()) - (set(POSSIBLE_DIRECT_FILTERS) | set(POSSIBLE_INDIRECT_FILTERS))
    request['filters'] = {k for k, v in request['filters'].items() if k not in unexpected_filters}

    query=get_query(request)
    filters=request.get('filters')

    if request.get('filters'):
        direct_filters,indirect_filters=get_applicable_filters(filters,POSSIBLE_DIRECT_FILTERS,POSSIBLE_INDIRECT_FILTERS)

    query=get_filters(direct_filters,query,AirFreightRate)
    query=apply_indirect_filters(query,indirect_filters)

    if request.get('return_query'):
        return {
            'list':query
        }
    data=get_data(query)
    pagination_data=get_pagination_data(query)

    # { list: data }.merge!(pagination_data)

def get_query(request):
    if request.get('all_rates_for_cogo_assured'):
       query=AirFreightRate.select(AirFreightRate.id, AirFreightRate.origin_airport_id, AirFreightRate.destination_airport_id, AirFreightRate.commodity, AirFreightRate.operation_type, AirFreightRate.stacking_type).where(AirFreightRate.updated_at > datetime.now()-timedelta(days=1) , AirFreightRate.validities != [] , AirFreightRate.rate_not_available_entry ==False)
       return query
    all_fields=list(AirFreightRate._meta.fields.keys())

    # if request.get('older_rates_required'):
    query =  AirFreightRate.select().from_(AirFreightRate).order_by(AirFreightRate.updated_at.desc()).where(((AirFreightRate.validities['status'].is_null(True))or (AirFreightRate.validity['status'] == 'true')) and (not((AirFreightRate.validity['validity_end'] > datetime.date.today()) and(AirFreightRate.validity['validity_end'] <= datetime.date.today())))).paginate(request.get('page'), request.get('page_limit'))

    # query=AirFreightRate.select().from_(AirFreightRate).order_by(AirFreightRate.updated_at.desc()).where((AirFreightRate.validities['validity_end']))

    return query

def get_data(query):
   
   
   return
   

def apply_updated_at_filer(query,filters):
   query.where(AirFreightRate.updated_at > filters['updated_at'])   
   return query

# def apply_location_ids_filter(query,filters):
#     location_ids = filters['location_ids']
#     query.where(AirFreightRate.location_ids.contains(location_ids))
#     return query

def apply_origin_location_ids_filter(query, filters):
  locations_ids = filters['origin_location_ids']
  query = query.where(AirFreightRate.origin_location_ids.contains(locations_ids))
  return query

def apply_destination_location_ids_filter(query,filters):
  locations_ids = filters['destination_location_ids']
  query = query.where(AirFreightRate.destination_location_ids.contains(locations_ids))
  return query

def apply_is_rate_about_to_expire_filter(query, filters):
  query = query.where(AirFreightRate.last_rate_available_date != None).where(AirFreightRate.last_rate_available_date >= datetime.now().date()).where(AirFreightRate.last_rate_available_date < (datetime.now().date() + timedelta(days = SEARCH_START_DATE_OFFSET)))
  return query

def apply_is_rate_not_available_filter(query,filters):
  query = query.where((AirFreightRate.last_rate_available_date == None) | (AirFreightRate.last_rate_available_date < datetime.now().date()))
  return query

def apply_is_rate_available_filter(query, filters):
  query = query.where(AirFreightRate.last_rate_available_date >= datetime.now().date())
  return query 

def apply_density_category_filter(query,filters):
    density_category = filters['density_category']
    if density_category == 'general':
        query=query.where("air_freight_rates.validity->>'density_category' = ? or (air_freight_rates.validity->>'density_category' is null)", 'general')
    else:
       query= query.where("air_freight_rates.validity->>'density_category' = ? and (air_freight_rates.validity->>'density_category' is not null)", density_category.to_s)

def apply_is_rate_not_available_entry_filter(query,filters):
   query=query.where(AirFreightRate.rate_not_available_entry==False)
   return query

def apply_last_rate_available_date_greater_than_filter(query,filters):
    query=query.where(AirFreightRate.last_rate_available_date> filters['last_rate_available_date_greater_than'])
    return query

def apply_procured_by_id_filter(query,filters):
   query = query.where(AirFreightRate.procured_by_id == filters['procured_by_id'])
   return query

def apply_partner_id_filter(query, filters):
  cogo_entity_id = filters['partner_id']
  if cogo_entity_id:
    query = query.where(AirFreightRate.cogo_entity_id.in_([cogo_entity_id,None]))
  else:
    query = query.where(AirFreightRate.cogo_entity_id == None)
  return query






def get_pagination_data(query, page, page_limit, pagination_data_required):
    if not pagination_data_required:
        return {}
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
    apply_filter_function = f'apply_{key}_filter'
    query = eval(f'{apply_filter_function}(query, filters)')
  return query

    
    
    




