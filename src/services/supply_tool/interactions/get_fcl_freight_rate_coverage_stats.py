from services.supply_tool.models.fcl_freight_rate_jobs import FclFreightRateJobs
import json
from libs.get_applicable_filters import get_applicable_filters
from libs.get_filters import get_filters
from libs.json_encoder import json_encoder

possible_direct_filters = ['origin_port_id','destination_port_id','shipping_line_id','commodity','status']
possible_indirect_filters = ['updated_at', 'user_id']

def get_fcl_freight_rate_stats(filters = {}, page_limit = 10, page = 1, sort_by = 'updated_at', sort_type = 'desc'):
    query = get_query(sort_by, sort_type)

    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)

        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)

        query = get_filters(direct_filters, query, FclFreightRateJobs)
        query = apply_indirect_filters(query, indirect_filters)

    statistics = {
      'pending': 0,
      'backlog': 0,
      'completed': 0,
      'spot_search' : 0,
      'critical_port_pair' : 0,
      'expiring_rates' : 0,
      'monitoring_dashboard' : 0,
      'cancelled_shipment' : 0,
      'total' : 0
    }

    if not query:
       return statistics

    data = get_data(query,statistics)

    return data


def get_query(sort_by, sort_type):
    query = FclFreightRateJobs.select()
    if sort_by:
        query = query.order_by(eval('FclFreightRateJobs.{}.{}()'.format(sort_by,sort_type)))
    return query

def get_data(query,statistics):
    raw_data = json_encoder(list(query.dicts()))
    statistics['total'] = len(raw_data)
    for item in raw_data:
        status = item['status']
        if status in statistics:
           statistics[status] += 1

        source = item['source']
        if source in statistics:
           statistics[source] += 1


    return statistics

def apply_indirect_filters(query, filters):
  for key in filters:
    apply_filter_function = f'apply_{key}_filter'
    query = eval(f'{apply_filter_function}(query, filters)')
  return query

def apply_updated_at_filter(query, filters):
  query = query.where(FclFreightRateJobs.updated_at > filters['updated_at'])
  return query

def apply_user_id_filter(query, filters):
   query = query.where(FclFreightRateJobs.assigned_to_id == filters['user_id'])
