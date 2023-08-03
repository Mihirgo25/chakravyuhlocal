from services.ftl_freight_rate.models.ftl_freight_rate import FtlFreightRate
from libs.get_filters import get_filters
from libs.get_applicable_filters import get_applicable_filters
import json
from math import ceil
from datetime import datetime, timedelta
from micro_services.client import common
from fastapi.encoders import jsonable_encoder

POSSIBLE_DIRECT_FILTERS = ['id','origin_location_id','origin_cluster_id','origin_city_id','destination_location_id','destination_cluster_id','destination_city_id','service_provider_id','importer_exporter_id','truck_type','truck_body_type','commodity','is_line_items_info_messages_present','is_line_items_error_messages_present','trip_type', 'rate_not_available_entry']

POSSIBLE_INDIRECT_FILTERS = ['origin_location_ids','destination_location_ids','importer_exporter_present','is_rate_available','procured_by_id','updated_at','validity_till']

def list_ftl_freight_rates(filters = {}, page_limit = 10, page = 1, return_query = False, pagination_data_required = False, all_rates_for_cogo_assured = False):
    query = get_query(all_rates_for_cogo_assured)
    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)

        direct_filters, indirect_filters = get_applicable_filters(filters, POSSIBLE_DIRECT_FILTERS, POSSIBLE_INDIRECT_FILTERS)

        query = get_filters(direct_filters, query, FtlFreightRate)
        query = apply_indirect_filters(query, indirect_filters)

    total_count = query.count()

    if page_limit:
      query = query.paginate(page, page_limit)

    data = get_data(query)
    pagination_data = get_pagination_data(query, page, page_limit, pagination_data_required, total_count)

    return {'list': data } | (pagination_data)

def get_query(all_rates_for_cogo_assured):
   if all_rates_for_cogo_assured:
    query = FtlFreightRate.select(
       FtlFreightRate.id,
       FtlFreightRate.origin_location_id,
       FtlFreightRate.destination_location_id,
       FtlFreightRate.truck_type,
       FtlFreightRate.trip_type,
       FtlFreightRate.commodity,
       FtlFreightRate.line_items
       ).where(
       FtlFreightRate.updated_at > datetime.now() - timedelta(days = 1),
       FtlFreightRate.line_items != '[]',
       ~FtlFreightRate.rate_not_available_entry,
       ~FtlFreightRate.is_line_items_error_messages_present
       )
    return query

   query = FtlFreightRate.select()
   query = query.order_by(eval('FtlFreightRate.{}.{}()'.format('updated_at','desc')))

   return query

def get_data(query):
  final_data = []
  data = jsonable_encoder(list(query.dicts()))

  for object in data:
    if object['line_items']:
      line_item = next((line_item for line_item in object['line_items'] if line_item['code'] == 'BAS'), None)

      if line_item:
        object['total_price'] = line_item['price']
        object['unit'] = line_item['unit']
        object['currency'] = line_item['currency']

    final_data.append(object)
  return final_data

def get_pagination_data(query, page, page_limit, pagination_data_required, total_count):
    if not pagination_data_required:
        return {}

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

def apply_origin_location_ids_filter(query, filters):
  locations_ids = filters['origin_location_ids']
  query = query.where(FtlFreightRate.origin_location_ids.contains(locations_ids))
  return query

def apply_destination_location_ids_filter(query,filters):
  locations_ids = filters['destination_location_ids']
  query = query.where(FtlFreightRate.destination_location_ids.contains(locations_ids))
  return query

def apply_importer_exporter_present_filter(query, filters):
  if filters['importer_exporter_present']:
    return query.where(FtlFreightRate.importer_exporter_id != None)

def apply_is_rate_available_filter(query, filters):
    rate_not_available_entry = not filters.get('is_rate_available')
    query = query.where(FtlFreightRate.rate_not_available_entry == rate_not_available_entry)
    return query

def apply_procured_by_id_filter(query, filters):
  query = query.where(FtlFreightRate.procured_by_id == filters['procured_by_id'])
  return query

def apply_updated_at_filter(query, filters):
  query = query.where(FtlFreightRate.updated_at > filters['updated_at'])
  return query

def apply_validity_till_filter(query, filters):
  query = query.where((FtlFreightRate.validity_start <= filters['validity_till']) & (FtlFreightRate.validity_end >= filters['validity_till']))
  return query
