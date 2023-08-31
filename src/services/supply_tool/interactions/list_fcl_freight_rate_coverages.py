from services.supply_tool.models.fcl_freight_rate_jobs import FclFreightRateJobs
import json
from libs.get_applicable_filters import get_applicable_filters
from libs.get_filters import get_filters
from libs.json_encoder import json_encoder

possible_direct_filters = ['origin_port_id','destination_port_id','shipping_line_id','commodity','status']
possible_indirect_filters = ['updated_at', 'user_id', 'date_range']

def list_fcl_freight_rate_coverages(filters = {}, page_limit = 10, page = 1, sort_by = 'updated_at', sort_type = 'desc'):
    query = get_query(sort_by, sort_type)
    if filters:
        if type(filters) != dict:
           filters = json.loads(filters)
        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)
        query = get_filters(direct_filters, query, FclFreightRateJobs)
        query = apply_indirect_filters(query, indirect_filters)
        
    if page_limit:
       query = query.paginate(page, page_limit)

    data = get_data(query)

    return { 'list': data } 

def get_data(query):
   return list(query.dicts())
   

def get_query(sort_by, sort_type):
  query = FclFreightRateJobs.select()
  if sort_by:
    query = query.order_by(eval('FclFreightRateJobs.{}.{}()'.format(sort_by,sort_type)))

  return query

def apply_indirect_filters(query, filters):
  for key in filters:
    apply_filter_function = f'apply_{key}_filter'
    query = eval(f'{apply_filter_function}(query, filters)')
  return query

def apply_user_id_filter(query, filters):
   query = query.where(FclFreightRateJobs.assigned_to_id == filters['user_id'])

def apply_updated_at_filter(query, filters):
  query = query.where(FclFreightRateJobs.updated_at > filters['updated_at'])
  return query


def apply_date_range_filter(query, filters):
    start_date = filters['date_range']['startDate']
    end_date = filters['date_range']['endDate']
    query = query.where(
        FclFreightRateJobs.updated_at.between(start_date, end_date)
    )
    return query