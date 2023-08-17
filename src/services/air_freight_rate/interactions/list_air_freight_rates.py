from datetime import datetime,timedelta
import json
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from libs.get_applicable_filters import get_applicable_filters
from libs.get_filters import get_filters
from math import ceil
from configs.global_constants import SEARCH_START_DATE_OFFSET
from services.air_freight_rate.helpers.air_freight_rate_card_helper import get_density_wise_rate_card
from peewee import fn, SQL
from libs.json_encoder import json_encoder

DEFAULT_INCLUDES = ['id', 'origin_airport_id', 'destination_airport_id', 'airline_id', 'commodity', 'commodity_type', 'commodity_sub_type', 'operation_type', 'service_provider_id', 'length', 'breadth', 'height', 'updated_at', 'created_at', 'maximum_weight', 'shipment_type', 'stacking_type', 'price_type', 'cogo_entity_id', 'rate_type', 'source', 'origin_airport', 'destination_airport', 'service_provider', 'airline', 'procured_by','importer_exporter_id','importer_exporter']

POSSIBLE_DIRECT_FILTERS = ['id', 'origin_airport_id', 'origin_country_id', 'origin_trade_id', 'origin_continent_id', 'destination_airport_id', 'destination_country_id', 'destination_trade_id', 'destination_continent_id', 'airline_id', 'commodity', 'operation_type', 'service_provider_id', 'rate_not_available_entry', 'price_type', 'shipment_type', 'stacking_type', 'commodity_type', 'cogo_entity_id', 'rate_type','source','importer_exporter_id','price_type']

POSSIBLE_INDIRECT_FILTERS = ['location_ids', 'is_rate_about_to_expire', 'is_rate_available', 'is_rate_not_available', 'last_rate_available_date_greater_than', 'procured_by_id', 'is_rate_not_available_entry', 'origin_location_ids', 'destination_location_ids', 'density_category', 'partner_id', 'available_volume_range', 'available_gross_weight_range', 'achieved_volume_percentage', 'achieved_gross_weight_percentage', 'updated_at','not_predicted_rate','date']


def list_air_freight_rates(revenue_desk_data_required=None,filters = {}, page_limit = 10, page = 1, sort_by = 'updated_at', sort_type = 'desc', return_query = False, older_rates_required = False,all_rates_for_cogo_assured = False,pagination_data_required = True, includes = {}):

  query = get_query(all_rates_for_cogo_assured, sort_by, sort_type, older_rates_required, includes)
  if filters:
    if type(filters) != dict:
      filters = json.loads(filters)

    direct_filters, indirect_filters = get_applicable_filters(filters, POSSIBLE_DIRECT_FILTERS, POSSIBLE_INDIRECT_FILTERS)
  
    query = get_filters(direct_filters, query, AirFreightRate)
    query = apply_indirect_filters(query, indirect_filters)

  pagination_data = get_pagination_data(query,page,page_limit,pagination_data_required)

  query = query.paginate(page,page_limit)
  data = get_data(query=query,revenue_desk_data_required=revenue_desk_data_required)
  return {'list':json_encoder(data) }| (pagination_data)


def get_query(all_rates_for_cogo_assured,sort_by, sort_type, older_rates_required, includes):
  if all_rates_for_cogo_assured:
     query=AirFreightRate.select(AirFreightRate.id, AirFreightRate.origin_airport_id, AirFreightRate.destination_airport_id, AirFreightRate.commodity, AirFreightRate.operation_type, AirFreightRate.stacking_type).where(AirFreightRate.updated_at > datetime.now()-timedelta(days=1) , AirFreightRate.validities != [] , AirFreightRate.rate_not_available_entry ==False)
     return query
  
  select_fields = []
  
  if includes and not isinstance(includes, dict):
    includes = json.loads(includes) 
    select_fields = list(includes.keys())
  else:
    select_fields = DEFAULT_INCLUDES
  
  fields = [getattr(AirFreightRate, key) for key in select_fields]
  query = (AirFreightRate
       .select(*fields, SQL('validity.value').alias('validity'))
       .from_(
           AirFreightRate,
           fn.jsonb_array_elements(AirFreightRate.validities).alias('validity')
       ))
  query = query.order_by(eval('AirFreightRate.{}.{}()'.format(sort_by,sort_type)))
  query = query.where(~AirFreightRate.rate_not_available_entry)
  query = query.where(AirFreightRate.last_rate_available_date >= datetime.now().date())
  query = query.where(SQL("TO_DATE(validity->>'validity_end','YYYY-MM-DD')") >= datetime.now().date())

  return query

def apply_indirect_filters(query, filters):
  for key in filters:
    if filters[key]:
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
  query = query.where(AirFreightRate.last_rate_available_date.is_null(False),
                      AirFreightRate.last_rate_available_date >= datetime.now().date(),
                      AirFreightRate.last_rate_available_date < (datetime.now().date() + timedelta(days = SEARCH_START_DATE_OFFSET)))
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
           (((SQL("validity->>'density_category'")) == density_category) |((SQL("validity->>'density_category'")).is_null(True)))
        )
    else:
        query=query.where(((SQL("validity->>'density_category'")) == density_category))
    return query

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

def apply_not_predicted_rate_filter(query,filters):
  query = query.where(AirFreightRate.source != 'predicted')
  return query

def apply_available_volume_range_filter(query,filters):
   if filters.get('rate_type') == 'market_place':
      return query
   query = query.where(
        ((SQL("CAST(validity->>'available_volume' as numeric)")) >= filters['available_volume_range']['min']),
        ((SQL("CAST(validity->>'available_volume' as numeric)")) <= filters['available_volume_range']['max'])
    
   )

   return query

def apply_available_gross_weight_range_filter(query,filters):
   if filters.get('rate_type') == 'market_place':
      return query
   query = query.where(
        ((SQL("CAST(validity->>'available_gross_weight' as numeric)")) >= filters['available_gross_weight_range']['min']),
        ((SQL("CAST(validity->>'available_gross_weight' as numeric)")) <= filters['available_gross_weight_range']['max'])
    
   )
   return query

def apply_achieved_volume_percentage_filter(query,filters):

   if filters.get('rate_type') == 'market_place':
      return query
   query = query.where(
        (((SQL("CAST(validity->>'available_volume' as numeric)")) / (SQL("CAST(validity->>'initial_volume' as numeric)"))) >= filters['achieved_volume_percentage']['min']),
        (((SQL("CAST(validity->>'available_volume' as numeric)")) / (SQL("CAST(validity->>'initial_volume' as numeric)"))) <= filters['achieved_volume_percentage']['max'])
    
   )

   return query

def apply_achieved_gross_weight_percentage_filter(query,filters):
   if filters.get('rate_type') == 'market_place':
      return query
   query = query.where(
        (((SQL("CAST(validity->>'available_gross_weight' as numeric)")) / (SQL("CAST(validity->>'available_gross_weight' as numeric)"))) >= filters['achieved_gross_weight_percentage']['min']),
        (((SQL("CAST(validity->>'available_gross_weight' as numeric)")) / (SQL("CAST(validity->>'available_gross_weight' as numeric)"))) <= filters['achieved_gross_weight_percentage']['max'])  
   )

   return query

def apply_date_filter(query,filters):
  date_to_apply = None
  try:
    date_to_apply = datetime.fromisoformat(filters['date']).date()
  except:
    date_to_apply = datetime.strptime(filters['date'], "%d-%m-%Y").date()
    
  if date_to_apply:
    query = query.where(
      (SQL("TO_DATE(validity->>'validity_end','YYYY-MM-DD')") >= date_to_apply),
      (SQL("TO_DATE(validity->>'validity_start','YYYY-MM-DD')") < date_to_apply)
    )
  
  return query

def get_data(query,revenue_desk_data_required):
    if revenue_desk_data_required:
      revenue_desk_data_required = json.loads(revenue_desk_data_required)

    results = []
    rates = json_encoder(list(query.dicts()))
    density_filter_hash = {}
    now = datetime.now()
    beginning_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    for rate in rates:
      validity = rate['validity']
      rate['weight_slabs'] = validity['weight_slabs']
      validity['min_price'] = float(validity.get('min_price') or 0)
      if validity.get('status') == None:
        validity['status'] = True
      if validity.get('density_category')==None:
          validity['density_category'] = 'general'
      if validity['density_category'] == 'general':
        validity['density_ratio'] = '1:1'
      else:
        validity['density_ratio'] = "1:{}".format(validity['min_density_weight'])
      validity_end = datetime.fromisoformat(validity['validity_end'])
      if validity.get('status') and not (validity_end > beginning_of_day and validity_end <= now):
        validity['validity_id'] = validity.get('id')
        if validity['validity_id']:
          del validity['id']
        rate = rate | validity
        rate['is_origin_local_missing'] = rate['origin_local']['is_line_items_error_messages_present'] if rate.get('origin_local') else None
        rate['is_destination_local_missing'] = rate['destination_local']['is_line_items_error_messages_present'] if rate.get('destination_local') else None
        if rate['price_type']!='all_in':
          rate['is_surcharge_missing'] = rate['surcharge']['is_line_items_error_messages_present'] if rate.get('surcharge') else None
      
      rate['line_items'] = []
      if revenue_desk_data_required:
         weight_slabs = rate['weight_slabs']
         chargeable_weight = revenue_desk_data_required['chargeable_weight']
         for slab in weight_slabs:
            if int(slab['lower_limit']) <= chargeable_weight and int(slab['upper_limit']) >chargeable_weight:
              rate['is_minimum_price_system_rate'] = (float(slab['tariff_price']) * float(chargeable_weight)) <= float(rate['validity']['min_price'] or 0)
              if rate['is_minimum_price_system_rate']:   
                line_item_price = rate['validity']['min_price']
                line_item_quantity = 1
              else:
                line_item_price = slab['tariff_price']
                line_item_quantity = chargeable_weight
              line_item = { 'code': 'BAS', 'unit': 'per_kg', 'price': line_item_price, 'quantity': line_item_quantity, 'currency': slab['currency'], 'total_price': line_item_price * line_item_quantity }
              rate['line_items'].append(line_item)
              rate['chargeable_weight'] = chargeable_weight
              rate['weight'] = revenue_desk_data_required['weight']
              rate['volume'] = revenue_desk_data_required['volume']
              break
      density_filter_hash = populate_density_filter_hash(density_filter_hash, rate, validity)
      results.append(rate)
      
    if revenue_desk_data_required:
      filter_rate_based_on_density(density_filter_hash,results,revenue_desk_data_required)
    results = sorted(results, key = lambda rate: rate['validity']['validity_end'], reverse=True)

    return results

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

def populate_density_filter_hash(density_filter_hash,rate,validity):
  key = rate['id']
  if key not in density_filter_hash.keys():
    density_filter_hash[rate['id']] = {}
    density_filter_hash[rate['id']]['freights'] = [validity]
  else:
    density_filter_hash[rate['id']]['freights'] = [validity] + density_filter_hash[rate['id']]['freights']
  return density_filter_hash


def filter_rate_based_on_density(density_filter_hash,responses,revenue_desk_data):
  gross_weight = revenue_desk_data.get('weight')
  gross_volume = revenue_desk_data.get('volume')
  trade_type = revenue_desk_data.get('trade_type')
  chargeable_weight = revenue_desk_data.get('chargeable_weight')
  final_list = []
  results = None
  for key,value in density_filter_hash.items():
    if value['freights']:
      results = get_density_wise_rate_card(value,trade_type, gross_weight, gross_volume, chargeable_weight)
    
    if not results:
        continue
    
    validity_ids = []
    for result in value['freights']:
        final_list.append("{}_{}".format(key,result['validity_id']))
  
  final_response = []
  for response in responses:
    key = "{}_{}".format(response['id'],response['validity_id'])
    if key in final_list and response['line_items']:
      final_response.append(response)
  
  return final_response

   
         

      
  

   