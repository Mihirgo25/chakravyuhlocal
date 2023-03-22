from services.fcl_freight_rate.models.fcl_freight_rate_local import FclFreightRateLocal
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from configs.global_constants import SEARCH_START_DATE_OFFSET
from datetime import datetime, timedelta
from services.fcl_freight_rate.helpers.find_or_initialize import apply_direct_filters
import json
from peewee import JOIN 
from playhouse.shortcuts import model_to_dict

possible_direct_filters = ['id', 'origin_port_id', 'origin_country_id', 'origin_trade_id', 'origin_continent_id', 'destination_port_id', 'destination_country_id', 'destination_trade_id', 'destination_continent_id', 'shipping_line_id', 'service_provider_id', 'importer_exporter_id', 'container_size', 'container_type', 'commodity', 'is_best_price', 'rate_not_available_entry', 'origin_main_port_id', 'destination_main_port_id', 'cogo_entity_id']
possible_indirect_filters = ['is_origin_local_missing', 'is_destination_local_missing', 'is_weight_limit_missing', 'is_origin_detention_missing', 'is_origin_plugin_missing', 'is_destination_detention_missing', 'is_destination_demurrage_missing', 'is_destination_plugin_missing', 'is_rate_about_to_expire', 'is_rate_available', 'is_rate_not_available', 'origin_location_ids', 'destination_location_ids', 'importer_exporter_present', 'last_rate_available_date_greater_than', 'validity_start_greater_than', 'validity_end_less_than', 'procured_by_id', 'partner_id']

def list_fcl_freight_rates(filters = {}, page_limit = 10, page = 1, sort_by = 'updated_at', sort_type = 'desc', return_query = False, expired_rates_required = False, all_rates_for_cogo_assured = False):
  query = get_query(all_rates_for_cogo_assured, sort_by, sort_type, page, page_limit)
  if filters:
    if type(filters) != dict:
      filters = json.loads(filters)
  
    query = apply_direct_filters(query, filters, possible_direct_filters, FclFreightRate)
    query = apply_indirect_filters(query, filters)

  if return_query:
    return {'list': [model_to_dict(item) for item in query.execute()]} 
    
  data = get_data(query,expired_rates_required)
  
  return {'list': data} 

def get_query(all_rates_for_cogo_assured, sort_by, sort_type, page, page_limit):
  if all_rates_for_cogo_assured:
    query = FclFreightRate.select(FclFreightRate.id, FclFreightRate.origin_port_id, FclFreightRate.origin_main_port_id, FclFreightRate.destination_port_id, FclFreightRate.destination_main_port_id, FclFreightRate.container_size, FclFreightRate.container_type, FclFreightRate.commodity
            ).where(FclFreightRate.updated_at > datetime.now() + timedelta(days = 1), FclFreightRate.validities != '[]', FclFreightRate.rate_not_available_entry == False, FclFreightRate.container_size in ['20', '40'])
    return query

  post_origin_locals = FclFreightRateLocal.select().alias('post_origin_locals')
  post_destination_locals = FclFreightRateLocal.select().alias('post_destination_locals')
  query = FclFreightRate.select(
    ).join(post_origin_locals, JOIN.LEFT_OUTER, on=(post_origin_locals.c.id == FclFreightRate.origin_local_id) 
      ).switch(FclFreightRate
        ).join(post_destination_locals, JOIN.LEFT_OUTER, on = (post_destination_locals.c.id == FclFreightRate.destination_local_id)
          ).order_by(eval('FclFreightRate.{}.{}()'.format(sort_by,sort_type))).paginate(page, page_limit)

  return query


def get_data(query, expired_rates_required):
  data = []

  for item in query.execute():
    result = {
    'id': str(item.id), 
    'origin_port_id': str(item.origin_port_id), 
    'origin_main_port_id': str(item.origin_main_port_id), 
    'destination_port_id': str(item.destination_port_id), 
    'destination_main_port_id': str(item.destination_main_port_id), 
    'shipping_line_id': str(item.shipping_line_id), 
    'service_provider_id': str(item.service_provider_id), 
    'destination_trade_id': str(item.destination_trade_id), 
    'origin_trade_id': str(item.origin_trade_id), 
    'importer_exporter_id': str(item.importer_exporter_id), 
    'container_size' : item.container_size, 
    'container_type' : item.container_type, 
    'commodity' : item.commodity, 
    'validities' : item.validities, 
    'is_best_price' : item.is_best_price, 
    'last_rate_available_date' : item.last_rate_available_date, 
    'containers_count' : item.containers_count, 
    'importer_exporters_count' : item.importer_exporters_count, 
    'weight_limit' : item.weight_limit, 
    'origin_local' : item.origin_local, 
    'destination_local' : item.destination_local, 
    'is_origin_local_line_items_error_messages_present' : item.is_origin_local_line_items_error_messages_present, 
    'origin_local_line_items_error_messages' : item.origin_local_line_items_error_messages, 
    'is_origin_local_line_items_info_messages_present' : item.is_origin_local_line_items_info_messages_present, 
    'origin_local_line_items_info_messages' : item.origin_local_line_items_info_messages,
    'is_destination_local_line_items_error_messages_present' : item.is_destination_local_line_items_error_messages_present, 
    'destination_local_line_items_error_messages' : item.destination_local_line_items_error_messages, 
    'is_destination_local_line_items_info_messages_present' : item.destination_local_line_items_error_messages, 
    'destination_local_line_items_info_messages' : item.destination_local_line_items_info_messages, 
    'is_origin_detention_slabs_missing' : item.is_origin_detention_slabs_missing, 
    'is_origin_demurrage_slabs_missing' : item.is_origin_demurrage_slabs_missing, 
    'is_origin_plugin_slabs_missing' : item.is_origin_plugin_slabs_missing, 
    'is_destination_detention_slabs_missing' : item.is_destination_detention_slabs_missing, 
    'is_destination_demurrage_slabs_missing' : item.is_destination_demurrage_slabs_missing, 
    'is_destination_plugin_slabs_missing' : item.is_destination_plugin_slabs_missing, 
    'procured_by_id' : item.procured_by_id,
    'sourced_by_id' : item.sourced_by_id,
    'cogo_entity_id': str(item.cogo_entity_id or ''),
    'shipping_line' : item.shipping_line,
    'origin_port' : item.origin_port, 
    'origin_main_port' : item.origin_main_port, 
    'destination_port' : item.destination_port, 
    'destination_main_port' : item.destination_main_port,
    'service_provider' : item.service_provider, 
    'importer_exporter' : item.importer_exporter, 
    'procured_by' : item.procured_by, 
    'sourced_by' : item.sourced_by
    }

    if item.origin_local_id:
      result = result | {'port_origin_local': {'data': item.origin_local_id.data, 'is_line_items_error_messages_present' :  item.origin_local_id.is_line_items_error_messages_present, 'line_items_error_messages' : item.origin_local_id.line_items_error_messages, 'is_line_items_info_messages_present' : item.origin_local_id.is_line_items_info_messages_present, 'line_items_info_messages' : item.origin_local_id.line_items_info_messages, 'is_detention_slabs_missing' : item.origin_local_id.is_detention_slabs_missing, 'is_demurrage_slabs_missing' : item.origin_local_id.is_demurrage_slabs_missing, 'is_plugin_slabs_missing' :  item.origin_local_id.is_plugin_slabs_missing}}
    if item.destination_local_id:
      result = result | {'port_destination_local': {'data': item.destination_local_id.data,'is_line_items_error_messages_present' :  item.destination_local_id.is_line_items_error_messages_present,'line_items_error_messages' : item.destination_local_id.line_items_error_messages,'is_line_items_info_messages_present' : item.destination_local_id.is_line_items_info_messages_present,'line_items_info_messages' : item.destination_local_id.line_items_info_messages,'is_detention_slabs_missing' : item.destination_local_id.is_detention_slabs_missing,'is_demurrage_slabs_missing' : item.destination_local_id.is_demurrage_slabs_missing,'is_plugin_slabs_missing' :  item.destination_local_id.is_plugin_slabs_missing}}

    if result['weight_limit']:
      if 'free_limit' in result['weight_limit']:
        result['is_weight_limit_missing'] = (result['weight_limit']['free_limit'] is None) 
    else:
      result['is_weight_limit_missing'] = True
    
    if 'port_origin_local' in result:
      result['is_origin_local_missing'] = (result['is_origin_local_line_items_error_messages_present'] != False) & (result['port_origin_local']['is_line_items_error_messages_present'] != False)
      if result['origin_local']:
        if result['origin_local'].get('detention') and result['port_origin_local']['data'].get('detention'):
          result['is_origin_detention_missing'] = (result['origin_local']['detention'].get('free_limit') is None) and ((result['port_origin_local']['data']['detention'].get('free_limit') is None))
        else:
          result['is_origin_detention_missing'] = True
          
        if result['origin_local'].get('plugin') and result['port_origin_local']['data'].get('plugin'):
          result['is_origin_plugin_missing'] = (result['origin_local']['plugin'].get('free_limit') is None and result['port_origin_local']['data'].get('plugin').get('free_limit') is None) if result['container_type'] == 'refer' else None
        else:
          result['is_origin_plugin_missing'] = True

      else:
        result['is_origin_detention_missing'] = True
        result['is_origin_plugin_missing'] = True

      del result['port_origin_local']

    if 'port_destination_local' in result:
        result['is_destination_local_missing'] = (result['is_destination_local_line_items_error_messages_present'] != False) & (result['port_destination_local']['is_line_items_error_messages_present'] != False)
        if result['destination_local']:
          if result['destination_local'].get('detention') and result['port_destination_local']['data'].get('detention'):
            result['is_destination_detention_missing'] = (result['destination_local']['detention'].get('free_limit') is None) and ((result['port_destination_local']['data'].get('detention').get('free_limit') is None))
          else:
            result['is_destination_detention_missing'] = True
          
          if result['destination_local'].get('plugin') and result['port_destination_local']['data'].get('plugin'):
            result['is_destination_plugin_missing'] = (result['destination_local']['plugin'].get('free_limit') is None and result['port_destination_local']['data']['plugin'].get('free_limit') is None) if result['container_type'] == 'refer' else None
          else:
            result['is_destination_plugin_missing'] = True
          
          result['is_destination_plugin_missing'] = (result['destination_local']['plugin'].get('free_limit') is None and result['port_destination_local']['data'].get('plugin').get('free_limit') is None) if result['container_type'] == 'refer' else None
          if result['destination_local'].get('demurrage') and result['port_destination_local']['data'].get('demurrage'):
            result['is_destination_demurrage_missing'] = (result['destination_local']['demurrage'].get('free_limit') is None) and ((result['port_destination_local']['data'].get('demurrage').get('free_limit') is None)) 
          else:
            result['is_destination_demurrage_missing'] = True
        del result['port_destination_local']

    validities = []
    
    if result['validities']:
      for validity_object in result['validities']:
        if (datetime.strptime(validity_object['validity_end'],'%Y-%m-%d') < datetime.now()) and (not expired_rates_required):
            continue 

        validity = {
          'validity_start': validity_object['validity_start'],
          'validity_end': validity_object['validity_end'],
          'price': validity_object['price'],
          'platform_price': validity_object['platform_price'],
          'currency': validity_object['currency'],
          'is_rate_about_to_expire': (datetime.strptime(validity_object['validity_end'],'%Y-%m-%d') >= datetime.now()) & (datetime.strptime(validity_object['validity_end'],'%Y-%m-%d') < (datetime.now() + timedelta(days = SEARCH_START_DATE_OFFSET))),
          'is_best_price': (validity_object['price'] == validity_object['platform_price']),
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
    if key in possible_indirect_filters:
      apply_filter_function = f'apply_{key}_filter'
      query = eval(f'{apply_filter_function}(query, filters)')
  return query

def apply_partner_id_filter(query, filters):
  cogo_entity_id = filters['partner_id']
  if cogo_entity_id:
    query = query.where(FclFreightRate.cogo_entity_id.in_([cogo_entity_id,None]))
  else:
    query = query.where(FclFreightRate.cogo_entity_id == None)
  return query

def apply_is_origin_local_missing_filter(query, filters):
  query = query.where((FclFreightRate.is_origin_local_line_items_error_messages_present == None) | (FclFreightRate.is_origin_local_line_items_error_messages_present == True)).where((FclFreightRateLocal.is_line_items_error_messages_present == None) | (FclFreightRateLocal.is_line_items_error_messages_present == True))
  return query


def apply_is_destination_local_missing_filter(query, filters):
  query = query.where((FclFreightRate.is_destination_local_line_items_error_messages_present == None) | (FclFreightRate.is_destination_local_line_items_error_messages_present == True)).where((FclFreightRateLocal.is_line_items_error_messages_present == None) | (FclFreightRateLocal.is_line_items_error_messages_present == True))
  return query


def apply_is_weight_limit_missing_filter(query, filters):
  query = query.where((FclFreightRate.is_weight_limit_slabs_missing == None) | (FclFreightRate.is_weight_limit_slabs_missing == True))
  return query


def apply_is_origin_detention_missing_filter(query, filters):
  query = query.where((FclFreightRate.is_origin_detention_slabs_missing == None) | (FclFreightRate.is_origin_detention_slabs_missing == True)).where((FclFreightRateLocal.is_detention_slabs_missing == None) | (FclFreightRateLocal.is_detention_slabs_missing == True))
  return query


def apply_is_origin_plugin_missing_filter(query,filters):
  query = query.where(FclFreightRate.container_type == 'refer').where((FclFreightRate.is_origin_plugin_slabs_missing == None) | (FclFreightRate.is_origin_plugin_slabs_missing == True)).where((FclFreightRateLocal.is_plugin_slabs_missing == None) | (FclFreightRateLocal.is_plugin_slabs_missing == True))
  return query


def apply_is_destination_detention_missing_filter(query,filters):
  query = query.where((FclFreightRate.is_destination_detention_slabs_missing == None) | (FclFreightRate.is_destination_detention_slabs_missing == True)).where((FclFreightRateLocal.is_detention_slabs_missing == None) | (FclFreightRateLocal.is_detention_slabs_missing == True))
  return query


def apply_is_destination_demurrage_missing_filter(query,filters):
  query = query.where((FclFreightRate.is_destination_demurrage_slabs_missing == None) | (FclFreightRate.is_destination_demurrage_slabs_missing == True)).where((FclFreightRateLocal.is_demurrage_slabs_missing == None) | (FclFreightRateLocal.is_demurrage_slabs_missing == True))
  return query


def apply_is_destination_plugin_missing_filter(query,filters):
  query = query.where((FclFreightRate.is_destination_plugin_slabs_missing == None) | (FclFreightRate.is_destination_plugin_slabs_missing == True)).where((FclFreightRateLocal.is_plugin_slabs_missing == None) | (FclFreightRateLocal.is_plugin_slabs_missing == None))
  return query


def apply_is_rate_about_to_expire_filter(query, filters):
  query = query.where(not (FclFreightRate.last_rate_available_date == None)).where(FclFreightRate.last_rate_available_date >= datetime.now().date()).where(FclFreightRate.last_rate_available_date < (datetime.now().date() + timedelta(days = SEARCH_START_DATE_OFFSET)))
  return query


def apply_is_rate_not_available_filter(query,filters):
  query = query.where((FclFreightRate.last_rate_available_date == None) or (FclFreightRate.last_rate_available_date < datetime.now().date()))
  return query


def apply_is_rate_available_filter(query, filters):
  query = query.where(FclFreightRate.last_rate_available_date >= datetime.now().date())
  return query 


def apply_origin_location_ids_filter(query, filters):
  locations_ids = filters['origin_location_ids']
  query = query.where(FclFreightRate.origin_location_ids.in_(locations_ids))
  return query


def apply_destination_location_ids_filter(query,filters):
  locations_ids = filters['destination_location_ids']
  query = query.where(FclFreightRate.destination_location_ids.in_(locations_ids))
  return query 


def apply_importer_exporter_present_filter(query, filters):
  if filters['importer_exporter_present']:
    return query.where(not (FclFreightRate.importer_exporter_id == None))
  
  query = query.where(FclFreightRate.importer_exporter_id == None)
  return query


def apply_last_rate_available_date_greater_than_filter(query, filters):
  query = query.where(FclFreightRate.last_rate_available_date >= datetime.strptime(filters['last_rate_available_date_greater_than'],'%Y-%m-%d'))
  return query


def apply_validity_start_greater_than_filter(query, filters):
  query = query.where(FclFreightRate.created_at >= datetime.strptime(filters['validity_start_greater_than'],'%Y-%m-%d'))
  return query


def apply_validity_end_less_than_filter(query,filters):
  query = query.where(FclFreightRate.created_at >= datetime.strptime(filters['validity_end_less_than'],'%Y-%m-%d'))
  return query

def apply_procured_by_id_filter(query, filters):
    query = query.where(FclFreightRate.procured_by_id == filters['procured_by_id'])
    return query

