from services.fcl_freight_rate.models.fcl_freight_rates import FclFreightRate
from services.fcl_freight_rate.models.fcl_freight_rate_audits import FclFreightRateAudit
from services.fcl_freight_rate.models.fcl_freight_rate_locals import FclFreightRateLocals

from configs.global_constants import SEARCH_START_DATE_OFFSET
from datetime import datetime, timedelta
import json
from operator import attrgetter
from peewee import JOIN, Case, Cast, DoesNotExist, fn


def to_dict(obj):
    return json.loads(json.dumps(obj, default=lambda o: o.__dict__))

def list_fcl_freight_rates(request):
  request = to_dict(request)

  query = get_query(request)
  query = apply_direct_filters(query, request['possible_direct_filters'])
  query = apply_indirect_filters(query, request['possible_indirect_filters'])

  if request['return_query']:
    return {'list': query.dicts().get()} 
    
  data = get_data(query,request)

  pagination_data = get_pagination_data(query, request)
  return {'list': data}.update(pagination_data)

def get_query(request):
    FCLLocalAlias = FclFreightRateLocals.alias()
    query = FclFreightRate.select(FclFreightRate, FclFreightRateLocals
      ).join(FclFreightRateLocals, JOIN.LEFT_OUTER, on=(FclFreightRateLocals.id == FclFreightRate.origin_local_id) 
        ).switch(FclFreightRate
           ).join(FCLLocalAlias, JOIN.LEFT_OUTER, on = (FCLLocalAlias.id == FclFreightRate.destination_local_id)
            ).order_by(eval('FclFreightRate.{}.{}()'.format(request['sort_by'],request['sort_type']))).paginate(request['page'], request['page_limit'])
    return query

def get_pagination_data(query, request):
  if not request['pagination_data_required']:
    return {}

  pagination_data = {
    'page': request['page'],
    'total': query.dicts()['total_pages'],
    'total_count': query.dicts()['total_count'],
    'page_limit': request['page_limit']
    }

  return pagination_data

def get_data(query, request):
  data = []
  results = query.select(FclFreightRate.id,FclFreightRate.origin_port_id,FclFreightRate.origin_main_port_id,FclFreightRate.destination_port_id,FclFreightRate.destination_main_port_id,FclFreightRate.shipping_line_id,FclFreightRate.service_provider_id,FclFreightRate.destination_trade_id,FclFreightRate.origin_trade_id,FclFreightRate.importer_exporter_id,FclFreightRate.container_size,FclFreightRate.container_type,FclFreightRate.commodity,FclFreightRate.validities,FclFreightRate.is_best_price,FclFreightRate.last_rate_available_date,FclFreightRate.containers_count,FclFreightRate.importer_exporters_count,FclFreightRate.priority_score,FclFreightRate.weight_limit,FclFreightRate.origin_local,FclFreightRate.destination_local,FclFreightRate.is_origin_local_line_items_error_messages_present,FclFreightRate.origin_local_line_items_error_messages,FclFreightRate.is_origin_local_line_items_info_messages_present,FclFreightRate.origin_local_line_items_info_messages,FclFreightRate.is_destination_local_line_items_error_messages_present,FclFreightRate.destination_local_line_items_error_messages,FclFreightRate.is_destination_local_line_items_info_messages_present,FclFreightRate.destination_local_line_items_info_messages,FclFreightRate.is_origin_detention_slabs_missing,FclFreightRate.is_origin_demurrage_slabs_missing,FclFreightRate.is_origin_plugin_slabs_missing,FclFreightRate.is_destination_detention_slabs_missing,FclFreightRate.is_destination_demurrage_slabs_missing,FclFreightRate.is_destination_plugin_slabs_missing,FclFreightRateLocals.data,FclFreightRateLocals.is_line_items_error_messages_present, FclFreightRateLocals.line_items_error_messages, FclFreightRateLocals.is_line_items_info_messages_present, FclFreightRateLocals.line_items_info_messages, FclFreightRateLocals.is_detention_slabs_missing, FclFreightRateLocals.is_demurrage_slabs_missing, FclFreightRateLocals.is_plugin_slabs_missing).dicts().get()
  rate_audits = FclFreightRateAudit.select().where(FclFreightRateAudit.object_id == result['id'], FclFreightRateAudit.object_type == 'FclFreightRate').dicts()

  for result in results:
    result['origin_local'] = dict(result['origin_local'])    
    result['destination_local'] = dict(result['destination_local'])
    result['port_origin_local'] = dict(result['port_origin_local'])
    result['port_destination_local'] = dict(result['port_destination_local'])

    result['weight_limit'] = dict(result['weight_limit'])
    result['is_weight_limit_missing'] = (result['weight_limit']['free_limit'] is None) 

    result['is_origin_local_missing'] = (result['is_origin_local_line_items_error_messages_present'] != False) & (result['port_origin_local']['is_line_items_error_messages_present'] != False)
    result['is_destination_local_missing'] = (result['is_destination_local_line_items_error_messages_present'] != False) & (result['port_destination_local']['is_line_items_error_messages_present'] != False)

    result['is_origin_detention_missing'] = (result['origin_local']['detention'].get('free_limit') is None) and (result['port_origin_local']['data'].get('detention').get('free_limit') is None)
    result['is_destination_detention_missing'] = (result['destination_local']['detention'].get('free_limit') is None) and (result['port_destination_local']['data'].get('detention').get('free_limit') is None)

    result['is_origin_plugin_missing'] = (result['origin_local']['plugin'].get('free_limit') is None and result['port_origin_local']['data'].get('plugin').get('free_limit') is None) if result['container_type'] == 'refer' else None
    result['is_destination_plugin_missing'] = (result['destination_local']['plugin'].get('free_limit') is None and result['port_destination_local']['data'].get('plugin').get('free_limit') is None) if result['container_type'] == 'refer' else None
    result['is_destination_demurrage_missing'] = (result['destination_local']['demurrage'].get('free_limit') is None) and (result['port_destination_local']['data'].get('demurrage').get('free_limit') is None)

  validities = []
      
  for validity_object in result['validities']:
    if (datetime.strptime(validity_object['validity_end'],'%Y-%m-%d %H:%M:%S.%f') < datetime.now()) & (not request['expired_rates_required']):
        continue 

    validities.append({
      'validity_start': validity_object['validity_start'],
      'validity_end': validity_object['validity_end'],
      'price': validity_object['price'],
      'platform_price': validity_object['platform_price'],
      'currency': validity_object['currency'],
      'is_rate_about_to_expire': (datetime.strptime(validity_object['validity_end'],'%Y-%m-%d %H:%M:%S.%f') >= datetime.now()) & (datetime.strptime(validity_object['validity_end'],'%Y-%m-%d %H:%M:%S.%f') < (datetime.now() + timedelta(days = SEARCH_START_DATE_OFFSET)).date()),
      'is_best_price': (validity_object['price'] == validity_object['platform_price']),
      'schedule_type': validity_object['schedule_type'],
      'payment_term': validity_object['payment_term'],
      'is_rate_expired': datetime.strptime(validity_object['validity_end'],'%Y-%m-%d %H:%M:%S.%f') < datetime.now()
    })

    result['validities'] = validities

    result['is_rate_not_available'] = (validities.count == 0)

    rate_audit = sorted([audit for audit in rate_audits if audit['object_id'] == result['id']], key=lambda x: x['created_at']).pop()

    result['sourced_by_id'] = rate_audit['sourced_by_id']
    result['procured_by_id'] = rate_audit['procured_by_id']

    del result['origin_local']
    del result['destination_local']
    del result['port_origin_local']
    del result['port_destination_local']

    data.append(result)

  # data = add_service_objects(data)

  return data

# # def add_service_objects(data):
# #   if data.count == 0:
# #       return data
  
# #   service_objects = GetMultipleServiceObjectsData.run!('objects': [
# #     {
# #       name: 'operator',
# #       filters: { id: data.pluck(:shipping_line_id).uniq },
# #       fields: [:id, :business_name, :short_name, :logo_url]
# #     },
# #     {
# #       name: 'location',
# #       filters: { id: data.map { |t| [t[:origin_port_id], t[:origin_main_port_id], t[:destination_port_id], t[:destination_main_port_id]] }.flatten.uniq },
# #       fields: [:id, :name, :display_name, :port_code, :type, :is_icd]
# #     },
# #     {
# #       name: 'organization',
# #       filters: { id: data.map { |t| [t[:service_provider_id], t[:importer_exporter_id]] }.flatten.uniq },
# #       fields: [:id, :business_name, :short_name]
# #     },
# #     {
# #       name: 'user',
# #       filters: { id: data.map { |t| [t[:procured_by_id], t[:sourced_by_id]] }.flatten.compact.uniq },
# #       fields: [:id, :name, :email]
# #     }
# #   ])
  
# #   for object in data:
# #     object[:shipping_line] = service_objects[:operator][object[:shipping_line_id].to_sym] rescue nil
# #     object[:origin_port] = service_objects[:location][object[:origin_port_id].to_sym] rescue nil
# #     object[:origin_main_port] = service_objects[:location][object[:origin_main_port_id].to_sym] rescue nil
# #     object[:destination_port] = service_objects[:location][object[:destination_port_id].to_sym] rescue nil
# #     object[:destination_main_port] = service_objects[:location][object[:destination_main_port_id].to_sym] rescue nil
# #     object[:service_provider] = service_objects[:organization][object[:service_provider_id].to_sym] rescue nil
# #     object[:importer_exporter] = service_objects[:organization][object[:importer_exporter_id].to_sym] rescue nil
# #     object[:procured_by] = service_objects[:user][object[:procured_by_id].to_sym] rescue nil
# #     object[:sourced_by] = service_objects[:user][object[:sourced_by_id].to_sym] rescue nil
# #     object

# #   return None

def apply_direct_filters(query,direct_filters):
  direct_filter = []
  for filter in direct_filters:
    if direct_filters[filter] != None:
      direct_filter.append(filter)
  
  for key in direct_filters:
    if key in direct_filter:
      query = query.select().where(attrgetter(key)(FclFreightRate) == direct_filters[key])
  return query


def apply_indirect_filters(query, indirect_filters):
  indirect_filter = []
  for filter in indirect_filters:
    if indirect_filters[filter] != None:
      indirect_filter.append(filter)

  for key in indirect_filters:
    if key in indirect_filter:
      apply_filter_function = f'apply_{key}_filter'
      query = eval(f'{apply_filter_function}(query, indirect_filters)')
  return query


def apply_is_origin_local_missing_filter(query, indirect_filters):
  query = query.where((FclFreightRate.is_origin_local_line_items_error_messages_present == None) | (FclFreightRate.is_origin_local_line_items_error_messages_present == True)).where((FclFreightRateLocals.is_line_items_error_messages_present == None) | (FclFreightRateLocals.is_line_items_error_messages_present == True))
  return query


def apply_is_destination_local_missing_filter(query, indirect_filters):
  query = query.where((FclFreightRate.is_destination_local_line_items_error_messages_present == None) | (FclFreightRate.is_destination_local_line_items_error_messages_present == True)).where((FclFreightRateLocals.is_line_items_error_messages_present == None) | (FclFreightRateLocals.is_line_items_error_messages_present == True))
  return query


def apply_is_weight_limit_missing_filter(query, indirect_filters):
  query = query.where((FclFreightRate.is_weight_limit_slabs_missing == None) | (FclFreightRate.is_weight_limit_slabs_missing == True))
  return query


def apply_is_origin_detention_missing_filter(query, indirect_filters):
  query = query.where((FclFreightRate.is_origin_detention_slabs_missing == None) | (FclFreightRate.is_origin_detention_slabs_missing == True)).where((FclFreightRateLocals.is_detention_slabs_missing == None) | (FclFreightRateLocals.is_detention_slabs_missing == True))
  return query


def apply_is_origin_plugin_missing_filter(query, indirect_filters):
  query = query.where(FclFreightRate.container_type == 'refer').where((FclFreightRate.is_origin_plugin_slabs_missing == None) | (FclFreightRate.is_origin_plugin_slabs_missing == True)).where((FclFreightRateLocals.is_plugin_slabs_missing == None) | (FclFreightRateLocals.is_plugin_slabs_missing == True))
  return query


def apply_is_destination_detention_missing_filter(query,indirect_filters):
  query = query.where((FclFreightRate.is_destination_detention_slabs_missing == None) | (FclFreightRate.is_destination_detention_slabs_missing == True)).where((FclFreightRateLocals.is_detention_slabs_missing == None) | (FclFreightRateLocals.is_detention_slabs_missing == True))
  return query


def apply_is_destination_demurrage_missing_filter(query,indirect_filters):
  query = query.where((FclFreightRate.is_destination_demurrage_slabs_missing == None) | (FclFreightRate.is_destination_demurrage_slabs_missing == True)).where((FclFreightRateLocals.is_demurrage_slabs_missing == None) | (FclFreightRateLocals.is_demurrage_slabs_missing == True))
  return query


def apply_is_destination_plugin_missing_filter(query,indirect_filters):
  query = query.where((FclFreightRate.is_destination_plugin_slabs_missing == None) | (FclFreightRate.is_destination_plugin_slabs_missing == True)).where((FclFreightRateLocals.is_plugin_slabs_missing == None) | (FclFreightRateLocals.is_plugin_slabs_missing == None))
  return query


def apply_is_rate_about_to_expire_filter(query, indirect_filters):
  query = query.where(not (FclFreightRate.last_rate_available_date == None)).where(FclFreightRate.last_rate_available_date >= datetime.now().date()).where(FclFreightRate.last_rate_available_date < (datetime.now().date() + timedelta(days = SEARCH_START_DATE_OFFSET)))
  return query


def apply_is_rate_not_available_filter(query,indirect_filters):
  query = query.where((FclFreightRate.last_rate_available_date == None) or (FclFreightRate.last_rate_available_date < datetime.now().date()))
  return query


def apply_is_rate_available_filter(query, indirect_filters):
  query = query.where(FclFreightRate.last_rate_available_date >= datetime.now().date())
  return query 


def apply_origin_location_ids_filter(query, indirect_filters):
  locations_ids = indirect_filters['origin_location_ids']
  query = query.where(FclFreightRate.origin_location_ids.in_(locations_ids))
  return query


def apply_destination_location_ids_filter(query,indirect_filters):
  locations_ids = indirect_filters['destination_location_ids']
  query = query.where(FclFreightRate.destination_location_ids.in_(locations_ids))
  return query 


def apply_importer_exporter_present_filter(query, indirect_filters):
  if indirect_filters['importer_exporter_present']:
    return query.where(not (FclFreightRate.importer_exporter_id == None))
  
  query = query.where(FclFreightRate.importer_exporter_id == None)
  return query


def apply_last_rate_available_date_greater_than_filter(query, indirect_filters):
  query = query.where(FclFreightRate.last_rate_available_date >= datetime.strptime(indirect_filters['last_rate_available_date_greater_than'],'%Y-%m-%d'))
  return query


def apply_validity_start_greater_than_filter(query, indirect_filters):
  query = query.where(FclFreightRate.created_at >= datetime.strptime(indirect_filters['validity_start_greater_than'],'%Y-%m-%d'))
  return query


def apply_validity_end_less_than_filter(query,indirect_filters):
  query = query.where(FclFreightRate.created_at >= datetime.strptime(indirect_filters['validity_end_less_than'],'%Y-%m-%d'))
  return query


def apply_procured_by_id_filter(query,indirect_filters):
    query = query.select().join(FclFreightRateAudit, JOIN.INNER_JOIN, on = (FclFreightRate.id == FclFreightRateAudit.object_id) & (FclFreightRateAudit.seqnum == 1)).where(FclFreightRateAudit.object_type == 'FclFreightRate', FclFreightRateAudit == indirect_filters['procured_by_id'])
    return query


def get_fcl_freight_rate_visibility_params(data):
  object = {
      'rate_id': data['id'],
      'service_provider_id': data['service_provider_id'],
      'from_date': data['validities'][0].get('validity_start') if data['validities'] else None,
      'to_date': data['validities'][0].get('validity_end') if data['validities'] else None,
      'shipping_line_id': data['shipping_line_id'],
      'origin_port_id': data['origin_port_id'],
      'destination_port_id': data['destination_port_id'],
      'origin_main_port_id': data['origin_main_port_id'],
      'destination_main_port_id': data['destination_main_port_id']
  }

  return object








