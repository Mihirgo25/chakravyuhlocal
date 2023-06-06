from datetime import datetime,timedelta
import json
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from libs.get_applicable_filters import get_applicable_filters
from libs.get_filters import get_filters
from math import ceil
from configs.global_constants import SEARCH_START_DATE_OFFSET
from peewee import fn, SQL,Window
from fastapi.encoders import jsonable_encoder

POSSIBLE_DIRECT_FILTERS = ['id', 'origin_airport_id', 'origin_country_id', 'origin_trade_id', 'origin_continent_id', 'destination_airport_id', 'destination_country_id', 'destination_trade_id', 'destination_continent_id', 'airline_id', 'commodity', 'operation_type', 'service_provider_id', 'rate_not_available_entry', 'price_type', 'shipment_type', 'stacking_type', 'commodity_type', 'cogo_entity_id', 'rate_type']

POSSIBLE_INDIRECT_FILTERS = ['location_ids', 'is_rate_about_to_expire', 'is_rate_available', 'is_rate_not_available', 'last_rate_available_date_greater_than', 'procured_by_id', 'is_rate_not_available_entry', 'origin_location_ids', 'destination_location_ids', 'density_category', 'partner_id', 'available_volume_range', 'available_gross_weight_range', 'achieved_volume_percentage', 'achieved_gross_weight_percentage', 'updated_at']


def list_air_freight_rate(filters = {}, page_limit = 10, page = 1, sort_by = 'updated_at', sort_type = 'desc', return_query = False, older_rates_required = False,all_rates_for_cogo_assured = False):

  query = get_query(all_rates_for_cogo_assured, sort_by, sort_type, page, page_limit,older_rates_required)
  if filters:
    if type(filters) != dict:
      filters = json.loads(filters)

    direct_filters, indirect_filters = get_applicable_filters(filters, POSSIBLE_DIRECT_FILTERS, POSSIBLE_INDIRECT_FILTERS)
  
    query = get_filters(direct_filters, query, AirFreightRate)
    query = apply_indirect_filters(query, indirect_filters)

    # { list: data }.merge!(pagination_data)

def get_query(all_rates_for_cogo_assured,sort_by, sort_type, page, page_limit,older_rates_required):
    if all_rates_for_cogo_assured:
       query=AirFreightRate.select(AirFreightRate.id, AirFreightRate.origin_airport_id, AirFreightRate.destination_airport_id, AirFreightRate.commodity, AirFreightRate.operation_type, AirFreightRate.stacking_type).where(AirFreightRate.updated_at > datetime.now()-timedelta(days=1) , AirFreightRate.validities != [] , AirFreightRate.rate_not_available_entry ==False)
       return query
    query = (
        AirFreightRate
        .select(AirFreightRate, fn.jsonb_array_elements(AirFreightRate.validities).alias('validity'))
        .where(AirFreightRate.rate_not_available_entry == False))
    
    # here
    if older_rates_required:
       query = query.where(
         ((query.c.validity['status']==True) | (query.c.validty['status'].is_null(True))),

       )
    query = query.order_by(eval('AirFreightRate.{}.{}()'.format(sort_by,sort_type))).paginate(page, page_limit)

def apply_indirect_filters(query, filters):
  for key in filters:
    apply_filter_function = f'apply_{key}_filter'
    query = eval(f'{apply_filter_function}(query, filters)')
  return query

   
def apply_updated_at_filer(query,filters):
   query.where(AirFreightRate.updated_at > datetime.fromisoformat(filters['updated_at']))   
   return query

# location ids column not there
def apply_location_ids_filter(query,filters):
    location_ids = filters['location_ids']
    query.where(AirFreightRate.location_ids.contains(location_ids))
    return query

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
        query=query.where(
           ((query.c.validty['density_category'] == density_category) |(query.c.validty['density_category'].is_null(True)))
        )
    else:
        ((query.c.validty['density_category'] == density_category) |(query.c.validty['density_category'].is_null(False)))

def apply_is_rate_not_available_entry_filter(query,filters):
   query=query.where(AirFreightRate.rate_not_available_entry==False)
   return query

def apply_last_rate_available_date_greater_than_filter(query,filters):
    query=query.where(AirFreightRate.last_rate_available_date > datetime.fromisoformat(filters['last_rate_available_date_greater_than']).date())
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

def apply_available_volume_range_filter(query,filters):
   if filters.get('rate_type') == 'general':
      return query
   query = query.where(
        (query.c.validity['available_volume'].cast('numeric') >= filters['available_volume_range']['min']),
        (query.c.validity['available_volume'].cast('numeric') <= filters['available_volume_range']['max'])
    
   )

   return query

def apply_available_gross_weight_range_filter(query,filters):
   if filters.get('rate_type') == 'general':
      return query
   query = query.where(
        (query.c.validity['available_gross_weight'].cast('numeric') >= filters['available_gross_weight']['min']),
        (query.c.validity['available_gross_weight'].cast('numeric') <= filters['available_gross_weight']['max'])
    
   )

   return query

def apply_achieved_volume_percentage_filter(query,filters):
   if filters.get('rate_type') == 'general':
      return query
   query = query.where(
        ((query.c.validity['available_volume'].cast('numeric') / query.c.validity['initial_volume'].cast('numeric')) >= filters['achieved_volume_percentage']['min']),
        ((query.c.validity['available_volume'].cast('numeric') / query.c.validity['initial_volume'].cast('numeric')) <= filters['achieved_volume_percentage']['max'])
    
   )

   return query

def apply_achieved_gross_weight_percentage_filter(query,filters):
   if filters.get('rate_type') == 'general':
      return query
   query = query.where(
        ((query.c.validity['available_gross_weight'].cast('numeric') / query.c.validity['initial_gross_weight'].cast('numeric')) >= filters['achieved_gross_weight_percentage']['min']),
        ((query.c.validity['available_gross_weight'].cast('numeric') / query.c.validity['initial_gross_weight'].cast('numeric')) <= filters['achieved_gross_weight_percentage']['max'])
    
   )

   return query

def get_data(query):
    results = []
    rates = jsonable_encoder(list(query.dicts()))

    now = datetime.now()
    beginning_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    for rate in rates:
      validity = rate['validity']
      if validity.get('status') == None:
        validity['status'] = True
        
      if validity.get('density_category')==None:
          validity['density_category'] = 'general'
      
      if validity['density_category'] == 'general':
        validity['density_ratio'] = '1:1'
      else:
        validity['density_ratio'] = "1:{}".format(int(validity['min_density_weight']))
      
      if validity.get('status') and not(validity.get('validity_end') > beginning_of_day and validity.get('validity_end') <= now):
         return
         








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



    
    
    




