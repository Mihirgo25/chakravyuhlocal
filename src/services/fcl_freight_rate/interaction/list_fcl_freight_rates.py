from services.fcl_freight_rate.models.fcl_freight_rate_local import FclFreightRateLocal
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from configs.global_constants import SEARCH_START_DATE_OFFSET
from datetime import datetime, timedelta
from libs.get_filters import get_filters
from libs.get_applicable_filters import get_applicable_filters
import json
from configs.fcl_freight_rate_constants import RATE_TYPES
from fastapi.encoders import jsonable_encoder

NOT_REQUIRED_FIELDS = ["destination_local_line_items_info_messages",  "origin_local_line_items_info_messages", "origin_local_line_items_error_messages", "destination_local_line_items_error_messages", "destination_location_ids", "origin_location_ids", "omp_dmp_sl_sp", "init_key"]

possible_direct_filters = ['id', 'origin_port_id', 'origin_country_id', 'origin_trade_id', 'origin_continent_id', 'destination_port_id', 'destination_country_id', 'destination_trade_id', 'destination_continent_id', 'shipping_line_id', 'service_provider_id', 'importer_exporter_id', 'container_size', 'container_type', 'commodity', 'is_best_price', 'rate_not_available_entry', 'origin_main_port_id', 'destination_main_port_id', 'cogo_entity_id', 'procured_by_id','rate_type']
possible_indirect_filters = ['is_origin_local_missing', 'is_destination_local_missing', 'is_weight_limit_missing', 'is_origin_detention_missing', 'is_origin_plugin_missing', 'is_destination_detention_missing', 'is_destination_demurrage_missing', 'is_destination_plugin_missing', 'is_rate_about_to_expire', 'is_rate_available', 'is_rate_not_available', 'origin_location_ids', 'destination_location_ids', 'importer_exporter_present', 'last_rate_available_date_greater_than', 'validity_start_greater_than', 'validity_end_less_than', 'partner_id', 'importer_exporter_relevant_rate']

def list_fcl_freight_rates(filters = {}, page_limit = 10, page = 1, sort_by = 'updated_at', sort_type = 'desc', return_query = False, expired_rates_required = False, all_rates_for_cogo_assured = False):
  query = get_query(all_rates_for_cogo_assured, sort_by, sort_type, page, page_limit)
  if filters:
    if type(filters) != dict:
      filters = json.loads(filters)

      if filters.get('rate_type') == 'all':
        filters['rate_type'] = RATE_TYPES
    direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)
  
    query = get_filters(direct_filters, query, FclFreightRate)
    query = apply_indirect_filters(query, indirect_filters)


  if return_query:
    return {'list': query} 
    
  data = get_data(query,expired_rates_required)
  
  return { 'list': data } 

def get_query(all_rates_for_cogo_assured, sort_by, sort_type, page, page_limit):
  if all_rates_for_cogo_assured:
    query = FclFreightRate.select(FclFreightRate.id, FclFreightRate.origin_port_id, FclFreightRate.origin_main_port_id, FclFreightRate.destination_port_id, FclFreightRate.destination_main_port_id, FclFreightRate.container_size, FclFreightRate.container_type, FclFreightRate.commodity
            ).where(FclFreightRate.updated_at > datetime.now() - timedelta(days = 1), FclFreightRate.validities != '[]', FclFreightRate.rate_not_available_entry == False, FclFreightRate.container_size << ['20', '40'])
    return query
  
  all_fields = list(FclFreightRate._meta.fields.keys())
  required_fields = [c for c in all_fields if c not in NOT_REQUIRED_FIELDS]
  fields = [getattr(FclFreightRate, key) for key in required_fields]
  
  query = FclFreightRate.select(*fields).order_by(eval('FclFreightRate.{}.{}()'.format(sort_by,sort_type))).paginate(page, page_limit)

  return query


def get_data(query, expired_rates_required):
  data = []

  raw_data = jsonable_encoder(list(query.dicts()))

  for result in raw_data:

    result['is_weight_limit_missing'] = False

    if not result['weight_limit'] or 'free_limit' not in result['weight_limit']:
      result['is_weight_limit_missing'] = True
    
    validities = []
    
    if result['validities']:
      for validity_object in result['validities']:
        if (datetime.strptime(validity_object['validity_end'],'%Y-%m-%d') <= datetime.now()) and (not expired_rates_required):
            continue 
        
        platform_price = validity_object.get('platform_price') or -1

        validity = {
          'validity_start': validity_object['validity_start'],
          'validity_end': validity_object['validity_end'],
          'price': validity_object['price'],
          'platform_price': platform_price,
          'currency': validity_object['currency'],
          'is_rate_about_to_expire': (datetime.strptime(validity_object['validity_end'],'%Y-%m-%d') >= datetime.now()) & (datetime.strptime(validity_object['validity_end'],'%Y-%m-%d') < (datetime.now() + timedelta(days = SEARCH_START_DATE_OFFSET))),
          'is_best_price': (validity_object['price'] == platform_price),
          'schedule_type' : validity_object['schedule_type'],
          'payment_type' : validity_object['payment_term'],
          'is_rate_expired' : datetime.strptime(validity_object['validity_end'],'%Y-%m-%d') < datetime.now()}
        
        validities.append(validity)
        result['validities'] = validities
      
        result['is_rate_not_available'] = (validities.count == 0)

      del result['origin_local']
      del result['destination_local']

    data.append(result)
  return data

def apply_indirect_filters(query, filters):
  for key in filters:
    apply_filter_function = f'apply_{key}_filter'
    query = eval(f'{apply_filter_function}(query, filters)')
  return query


def apply_importer_exporter_relevant_rate_filter(query, filters):
    importer_exporter_id = filters["importer_exporter_relevant_rate"]
    query = query.where((FclFreightRate.importer_exporter_id == importer_exporter_id) | (
        FclFreightRate.importer_exporter_id == None)
    )
    return query


def apply_partner_id_filter(query, filters):
  cogo_entity_id = filters['partner_id']
  if cogo_entity_id:
    query = query.where(FclFreightRate.cogo_entity_id.in_([cogo_entity_id,None]))
  else:
    query = query.where(FclFreightRate.cogo_entity_id == None)
  return query

def apply_is_origin_local_missing_filter(query, filters):
  is_messages = False
  if filters['is_origin_local_line_items_error_messages_present'] == True or filters['is_origin_local_line_items_error_messages_present'] == 'True':
    is_messages = True
  if is_messages:
    query =  query.where(FclFreightRate.is_origin_local_line_items_error_messages_present)
  else:
    query =  query.where((FclFreightRate.is_origin_local_line_items_error_messages_present == None | ~FclFreightRate.is_origin_local_line_items_error_messages_present))
  return query


def apply_is_destination_local_missing_filter(query, filters):
  is_messages = False
  if filters['is_destination_local_line_items_error_messages_present'] == True or filters['is_destination_local_line_items_error_messages_present'] == 'True':
    is_messages = True
  if is_messages:
    query =  query.where(FclFreightRate.is_destination_local_line_items_error_messages_present)
  else:
    query =  query.where((FclFreightRate.is_destination_local_line_items_error_messages_present == None | ~FclFreightRate.is_destination_local_line_items_error_messages_present))
  return query

def apply_is_weight_limit_missing_filter(query, filters):
  is_messages = False
  if filters['is_weight_limit_slabs_missing'] == True or filters['is_weight_limit_slabs_missing'] == 'True':
    is_messages = True
  if is_messages:
    query =  query.where(FclFreightRate.is_weight_limit_slabs_missing)
  else:
    query =  query.where((FclFreightRate.is_weight_limit_slabs_missing == None | ~FclFreightRate.is_weight_limit_slabs_missing))

  return query


def apply_is_origin_detention_missing_filter(query, filters):
  is_messages = False
  if filters['is_origin_detention_slabs_missing'] == True or filters['is_origin_detention_slabs_missing'] == 'True':
    is_messages = True
  if is_messages:
    query =  query.where(FclFreightRate.is_origin_detention_slabs_missing)
  else:
    query =  query.where((FclFreightRate.is_origin_detention_slabs_missing == None | ~FclFreightRate.is_origin_detention_slabs_missing))
  return query


def apply_is_origin_plugin_missing_filter(query,filters):
  is_messages = False
  if filters['is_origin_plugin_slabs_missing'] == True or filters['is_origin_plugin_slabs_missing'] == 'True':
    is_messages = True
  if is_messages:
    query =  query.where(FclFreightRate.is_origin_plugin_slabs_missing)
  else:
    query =  query.where((FclFreightRate.is_origin_plugin_slabs_missing == None | ~FclFreightRate.is_origin_plugin_slabs_missing))

  return query


def apply_is_destination_detention_missing_filter(query,filters):
  is_messages = False
  if filters['is_destination_detention_slabs_missing'] == True or filters['is_destination_detention_slabs_missing'] == 'True':
    is_messages = True
  if is_messages:
    query =  query.where(FclFreightRate.is_destination_detention_slabs_missing)
  else:
    query =  query.where((FclFreightRate.is_destination_detention_slabs_missing == None | ~FclFreightRate.is_destination_detention_slabs_missing))

  return query


def apply_is_destination_demurrage_missing_filter(query,filters):
  is_messages = False
  if filters['is_destination_demurrage_slabs_missing'] == True or filters['is_destination_demurrage_slabs_missing'] == 'True':
    is_messages = True
  if is_messages:
    query =  query.where(FclFreightRate.is_destination_demurrage_slabs_missing)
  else:
    query =  query.where((FclFreightRate.is_destination_demurrage_slabs_missing == None | ~FclFreightRate.is_destination_demurrage_slabs_missing))

  return query


def apply_is_destination_plugin_missing_filter(query,filters):
  is_messages = False
  if filters['is_destination_plugin_slabs_missing'] == True or filters['is_destination_plugin_slabs_missing'] == 'True':
    is_messages = True
  if is_messages:
    query =  query.where(FclFreightRate.is_destination_plugin_slabs_missing)
  else:
    query =  query.where((FclFreightRate.is_destination_plugin_slabs_missing == None | ~FclFreightRate.is_destination_plugin_slabs_missing))

  return query


def apply_is_rate_about_to_expire_filter(query, filters):
  query = query.where(FclFreightRate.last_rate_available_date != None).where(FclFreightRate.last_rate_available_date >= datetime.now().date()).where(FclFreightRate.last_rate_available_date < (datetime.now().date() + timedelta(days = SEARCH_START_DATE_OFFSET)))
  return query


def apply_is_rate_not_available_filter(query,filters):
  query = query.where((FclFreightRate.last_rate_available_date == None) | (FclFreightRate.last_rate_available_date < datetime.now().date()))
  return query


def apply_is_rate_available_filter(query, filters):
  query = query.where(FclFreightRate.last_rate_available_date >= datetime.now().date())
  return query 


def apply_origin_location_ids_filter(query, filters):
  locations_ids = filters['origin_location_ids']
  query = query.where(FclFreightRate.origin_location_ids.contains(locations_ids))
  return query


def apply_destination_location_ids_filter(query,filters):
  locations_ids = filters['destination_location_ids']
  query = query.where(FclFreightRate.destination_location_ids.contains(locations_ids))
  return query 


def apply_importer_exporter_present_filter(query, filters):
  if filters['importer_exporter_present']:
    return query.where(FclFreightRate.importer_exporter_id != None)
  
  query = query.where(FclFreightRate.importer_exporter_id == None)
  return query


def apply_last_rate_available_date_greater_than_filter(query, filters):
  query = query.where(FclFreightRate.last_rate_available_date >= datetime.fromisoformat(filters['last_rate_available_date_greater_than']).date())
  return query


def apply_validity_start_greater_than_filter(query, filters):
  query = query.where(FclFreightRate.created_at.cast('date') >= datetime.fromisoformat(filters['validity_start_greater_than']).date())
  return query


def apply_validity_end_less_than_filter(query,filters):
  query = query.where(FclFreightRate.created_at.cast('date') >= datetime.fromisoformat(filters['validity_end_less_than']).date())
  return query

def apply_procured_by_id_filter(query, filters):
  query = query.where(FclFreightRate.procured_by_id == filters['procured_by_id'])
  return query

