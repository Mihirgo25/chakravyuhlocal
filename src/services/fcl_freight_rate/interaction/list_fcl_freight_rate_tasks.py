from services.fcl_freight_rate.models.fcl_freight_rate_task import FclFreightRateTask
from services.fcl_freight_rate.models.fcl_freight_rate_local import FclFreightRateLocal
from services.fcl_freight_rate.helpers.find_or_initialize import apply_direct_filters
from configs.fcl_freight_rate_constants import *
from playhouse.shortcuts import model_to_dict
from configs.fcl_freight_rate_constants import EXPECTED_TAT
from math import ceil
from configs.definitions import FCL_FREIGHT_LOCAL_CHARGES
from peewee import fn
from datetime import datetime, timedelta
import concurrent.futures, json
from peewee import SQL 

possible_direct_filters = ['port_id', 'container_size', 'container_type', 'commodity', 'shipping_line_id', 'trade_type', 'status', 'task_type']
possible_indirect_filters = ['created_at_greater_than', 'created_at_less_than']

def list_fcl_freight_rate_tasks(filters = {}, page_limit = 10, page = 1, sort_by = 'created_at', sort_type = 'desc', stats_required = True, pagination_data_required = True):
    query = get_query(page, page_limit, sort_by, sort_type)

    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)

        query = apply_direct_filters(query, filters, possible_direct_filters, FclFreightRateTask)
        query = apply_indirect_filters(query, filters)

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(eval(method_name), query, filters, page, page_limit, pagination_data_required) for method_name in ['get_data', 'get_pagination_data']]
        results = {}
        for future in futures:
            result = future.result()
            results.update(result)
        
    data = results['get_data']
    pagination_data = results['get_pagination_data']

    stats = get_stats(filters, stats_required)

    return {'list': data } | (pagination_data) | (stats)
  

def get_query(page, page_limit, sort_by, sort_type):
    query = FclFreightRateTask.select().order_by(eval('FclFreightRateTask.{}.{}()'.format(sort_by, sort_type))).paginate(page, page_limit)
    return query
  
def get_pagination_data(query, filters, page, page_limit, pagination_data_required):
    if not pagination_data_required:
        return {'get_pagination_data': {}}

    params = {
      'page': page,
      'total': ceil(query.count()/page_limit),
      'total_count': query.count(),
      'page_limit': page_limit
    }
    return {'get_pagination_data' : params}

def get_data(query, filters, page, page_limit, pagination_data_required):
    new_data = []
    port_ids, main_port_ids, container_sizes, container_types, commodities, trade_types, shipping_line_ids = [],[], [],[], [],[], []
    for object in query.dicts():
        created_at_date = object['created_at']
        next_date = object['created_at'] + timedelta(days = 1)

        object['expiration_time'] = object['created_at'] + timedelta(seconds = EXPECTED_TAT * 60 * 60)
        object['skipped_time'] = 0

        if object['created_at'] < datetime.strptime("{} 09:30:00".format(str(created_at_date.date())), '%Y-%m-%d %H:%M:%S'):
            object['expiration_time'] = datetime.strptime("{} 09:30:00".format(str(created_at_date.date())), '%Y-%m-%d %H:%M:%S') + timedelta(seconds = EXPECTED_TAT * 60 * 60)
        elif object['created_at'] > datetime.strptime("{} 18:30:00".format(str(created_at_date.date())), '%Y-%m-%d %H:%M:%S'):
            object['expiration_time'] = datetime.strptime("{} 09:30:00".format(str(next_date.date())), '%Y-%m-%d %H:%M:%S') + timedelta(seconds = EXPECTED_TAT * 60 * 60)
        else:
            skipped_time = int((object['created_at'] + timedelta(seconds = EXPECTED_TAT * 60 * 60)).timestamp()) - int(datetime.strptime("{} 18:30:00".format(str(created_at_date.date())), '%Y-%m-%d %H:%M:%S').timestamp())
            skipped_time = max([0, skipped_time])
        
        if skipped_time > 0:
            object['expiration_time'] = datetime.strptime("{} 09:30:00".format(str(next_date.date())), '%Y-%m-%d %H:%M:%S') + timedelta(seconds = skipped_time) 
        
        if object['job_data']:
            object['purchase_invoice_rate'] = object['job_data'].get('rate')
        else:
            object['purchase_invoice_rate'] = None
        del object['job_data']

        port_ids.append(object['port_id'])
        main_port_ids.append(object['main_port_id']), 
        container_sizes.append(object['container_size']), 
        container_types.append(object['container_type']), 
        commodities.append(object['commodity']),
        trade_types.append(object['trade_type']) 
        shipping_line_ids.append(object['shipping_line_id'])
        new_data.append(object)

    if 'status' in filters and filters['status'] == 'completed':
        fcl_freight_local_charges = FCL_FREIGHT_LOCAL_CHARGES

        for object in new_data:
            rate = object['completion_data'].get('rate')

            rate['total_price'] = 0
            rate['total_price_currency'] = rate['line_items'][0]['currency'] or 'INR'
            
            for i in range(len(rate['line_items'])):
                rate['line_items'][i]['name'] = fcl_freight_local_charges[rate['line_items'][i]['code']]['name']

            object['rate'] = rate

            object['expiration_time'] = object['created_at'] + timedelta(hours = 6)

            object['completion_time'] = int(datetime.fromisoformat(object['completed_at']).timestamp()) - int(object['created_at'].timestamp())

            object['completed_at'] = str(datetime.fromisoformat(object['completed_at']))
            
            if object['completion_time'] < (2 * 60 * 60):
                object['remark'] = 'Super Fast' 
            if object['completion_time'] > (2 * 60 * 60) and object['completion_time'] <= (EXPECTED_TAT * 60 * 60):
                object['remark'] = 'On Time' 
            if object['completion_time'] > (EXPECTED_TAT * 60 * 60):
                object['remark'] = 'Delayed' 

            del object['completion_data']
    
    existing_system_query = FclFreightRateLocal.select().where(
      FclFreightRateLocal.port_id.in_(list(set(port_ids))),
      FclFreightRateLocal.main_port_id.in_(list(set(main_port_ids))),
      FclFreightRateLocal.container_size.in_(list(set(container_sizes))),
      FclFreightRateLocal.container_type.in_(list(set(container_types))),
      FclFreightRateLocal.commodity.in_(list(set(commodities))),
      FclFreightRateLocal.trade_type.in_(list(set(trade_types))),
      FclFreightRateLocal.shipping_line_id.in_(list(set(shipping_line_ids))),
      FclFreightRateLocal.service_provider_id == DEFAULT_SERVICE_PROVIDER_ID
    )
    existing_system_rates = [model_to_dict(item) for item in existing_system_query]
    
    for i in range(len(new_data)):
        new_data[i]['service_provider_id'] = DEFAULT_SERVICE_PROVIDER_ID
        new_data[i]['sourced_by_id'] = DEFAULT_SOURCED_BY_ID
        new_data[i]['procured_by_id'] = DEFAULT_PROCURED_BY_ID
        new_data[i]['existing_system_rate'] = None
        
        if existing_system_rates:
            existing_system_rate = list(filter(lambda rate: 
                                    rate['port_id'] == new_data[i]['port_id'] and
                                    rate['main_port_id'] == new_data[i]['main_port_id'] and
                                    rate['container_size'] == new_data[i]['container_size'] and
                                    rate['container_type'] == new_data[i]['container_type'] and
                                    rate['commodity'] == new_data[i]['commodity'] and
                                    rate['trade_type'] == new_data[i]['trade_type'] and
                                    rate['shipping_line_id'] == new_data[i]['shipping_line_id'],
                                existing_system_rates))


            if existing_system_rate:
                new_data[i]['existing_system_rate'] = existing_system_rate[0]['data']
                new_data[i]['existing_system_rate']['updated_at'] = existing_system_rate[0]['updated_at']
        else:
            new_data[i]['existing_system_rate'] = {}
            new_data[i]['existing_system_rate']['updated_at'] = None
            
    return {'get_data': new_data }


def apply_indirect_filters(query, filters):
    for key in filters:
        if key in possible_indirect_filters:
            apply_filter_function = f'apply_{key}_filter'
            query = eval(f'{apply_filter_function}(query, filters)')
    return query  

def apply_created_at_greater_than_filter(query, filters):
    query = query.where(FclFreightRateTask.updated_at >= datetime.strptime(filters['created_at_greater_than'], '%Y-%m-%d'))
    return query

def apply_created_at_less_than_filter(query, filters):
    query = query.where(FclFreightRateTask.updated_at <= datetime.strptime(filters['created_at_less_than'], '%Y-%m-%d'))
    return query

def get_stats(filters, stats_required):
    if not stats_required:
        return {}
    query = FclFreightRateTask.select()

    if filters:
        if 'trade_type' in filters:
            del filters['trade_type'] 
        
        if 'status' in filters:
            del filters['status']

        query = apply_direct_filters(query, filters, possible_direct_filters, FclFreightRateTask)
        query = apply_indirect_filters(query, filters)
    
    query = query.select(fn.COUNT(SQL('*')).alias('count_all'), FclFreightRateTask.status.alias('fcl_freight_task_status'), FclFreightRateTask.trade_type.alias('fcl_freight_task_trade_type')).group_by(FclFreightRateTask.status, FclFreightRateTask.trade_type)
    query_result = {}
    for i in query.execute():
        lists = [i.fcl_freight_task_status,i.fcl_freight_task_trade_type]
        query_result[tuple(lists)] = i.count_all

    stats = { 'pending': { 'export': 0, 'import': 0, 'total': 0 }, 'completed': { 'export': 0, 'import': 0, 'total': 0 }, 'aborted': { 'export': 0, 'import': 0, 'total': 0 } }
     
    for stat,count in query_result.items():
        stats[stat[0]][stat[1]] += count
        stats[stat[0]]['total'] += count

    return {
        'stats': stats
    }