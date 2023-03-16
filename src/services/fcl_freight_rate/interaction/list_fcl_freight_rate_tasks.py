from services.fcl_freight_rate.models.fcl_freight_rate_task import FclFreightRateTask
from services.fcl_freight_rate.models.fcl_freight_rate_local import FclFreightRateLocal
from services.fcl_freight_rate.helpers.find_or_initialize import apply_direct_filters
from libs.dynamic_constants.fcl_freight_rate_dc import FclFreightRateDc
from rails_client import client
from playhouse.shortcuts import model_to_dict
from configs.fcl_freight_rate_constants import EXPECTED_TAT
from math import ceil
from configs.defintions import FCL_FREIGHT_LOCAL_CHARGES
from peewee import fn
from datetime import datetime, timedelta
import yaml, concurrent.futures, json
from peewee import SQL 

possible_direct_filters = ['port_id', 'container_size', 'container_type', 'commodity', 'shipping_line_id', 'trade_type', 'status', 'task_type']
possible_indirect_filters = ['created_at_greater_than', 'created_at_less_than']

def list_fcl_freight_rate_tasks(filters, page_limit, page, sort_by, sort_type, stats_required, pagination_data_required):
    if type(filters) != dict:
        filters = json.loads(filters)
    query = get_query(page, page_limit, sort_by, sort_type)

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

    stats = get_stats(query, filters, page, page_limit, sort_by, sort_type, stats_required)

    return {'list': data } | (pagination_data) | (stats)
  

def get_query(page, page_limit, sort_by, sort_type):
    query = FclFreightRateTask.select().order_by(eval('FclFreightRateTask.{}.{}()()'.format(sort_by, sort_type))).paginate(page, page_limit)
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
    data = [model_to_dict(item) for item in query.execute()]
    
    new_data = []
    for object in data:
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

            object['expiration_time'] = datetime.strptime(object['created_at'], '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours = 6)
            
            object['completion_time'] = int(datetime.strptime(object['completed_at'], '%Y-%m-%d %H:%M:%S').strftime("%Y%m%d%H%M%S")) - int(datetime.strptime(object['created_at'], '%Y-%m-%d %H:%M:%S').strftime("%Y%m%d%H%M%S"))
            object['completed_at'] = str(datetime.strptime(object['completed_at'], '%Y-%m-%d %H:%M:%S'))
            
            if object['completion_time'] < (2 * 60 * 60):
                object['remark'] = 'Super Fast' 
            if object['completion_time'] > (2 * 60 * 60) and object['completion_time'] <= (EXPECTED_TAT * 60 * 60):
                object['remark'] = 'On Time' 
            if object['completion_time'] > (EXPECTED_TAT * 60 * 60):
                object['remark'] = 'Delayed' 

            del object['completion_data']

    new_data = add_service_objects(new_data)
    return {'get_data': new_data }
  
def add_service_objects(data):
    service_objects = client.ruby.get_multiple_service_objects_data_for_fcl({'objects': [
    {
        'name': 'operator',
        'filters': {'id': list(set(filter(None, [t['shipping_line_id'] for t in data]))) },
        'fields': ['id', 'business_name', 'short_name', 'logo_url']
    },
    {
        'name': 'location',
        'filters': {'id': list(set(filter(None, [d.get('port_id') for d in data] + [d.get('main_port_id') for d in data]))) }, 

        'fields': ['id', 'name', 'display_name', 'port_code', 'type']
    },
    {
        'name': 'user',
        'filters': {'id': list(set(filter(None, [t['completed_by_id'] for t in data])))}, 
        'fields': ['name', 'email']
    }
    ]})

    existing_system_query = FclFreightRateLocal.select().where(
      FclFreightRateLocal.port_id.in_(list(set([t['port_id'] for t in data]))),
      FclFreightRateLocal.main_port_id.in_(list(set([t['main_port_id'] for t in data]))),
      FclFreightRateLocal.container_size.in_(list(set([t['container_size'] for t in data]))),
      FclFreightRateLocal.container_type.in_(list(set([t['container_type'] for t in data]))),
      FclFreightRateLocal.commodity.in_(list(set([t['commodity'] for t in data]))),
      FclFreightRateLocal.trade_type.in_(list(set([t['trade_type'] for t in data])),
      FclFreightRateLocal.shipping_line_id.in_(list(set([t['shipping_line_id'] for t in data]))),
      FclFreightRateLocal.service_provider_id == FclFreightRateDc.get_key_value('DEFAULT_SERVICE_PROVIDER_ID')
    ))
    existing_system_rates = [model_to_dict(item) for item in existing_system_query]
    
    for i in range(len(data)):
        data[i]['shipping_line'] = service_objects['operator'][data[i]['shipping_line_id']] if 'operator' in service_objects and data[i].get('shipping_line_id') in service_objects['operator'] else None
        data[i]['port'] = service_objects['location'][data[i]['port_id']] if 'location' in service_objects and data[i].get('port_id') in service_objects['location'] else None
        data[i]['main_port'] = service_objects['location'][data[i]['main_port_id']] if 'location' in service_objects and data[i].get('main_port_id') in service_objects['location'] else None
        data[i]['completed_by'] = service_objects['user'][data[i]['completed_by_id']] if 'user' in service_objects and data[i].get('completed_by_id') in service_objects['user'] else None
        data[i]['service_provider_id'] = FclFreightRateDc.get_key_value('DEFAULT_SERVICE_PROVIDER_ID')
        data[i]['sourced_by_id'] = FclFreightRateDc.get_key_value('DEFAULT_SOURCED_BY_ID')
        data[i]['procured_by_id'] = FclFreightRateDc.get_key_value('DEFAULT_PROCURED_BY_ID')
        data[i]['existing_system_rate'] = None
    

        existing_system_rate = list(filter(lambda rate: 
                                rate['port_id'] == data[i]['port_id'] and
                                rate['main_port_id'] == data[i]['main_port_id'] and
                                rate['container_size'] == data[i]['container_size'] and
                                rate['container_type'] == data[i]['container_type'] and
                                rate['commodity'] == data[i]['commodity'] and
                                rate['trade_type'] == data[i]['trade_type'] and
                                rate['shipping_line_id'] == data[i]['shipping_line_id'],
                            existing_system_rates))[0]


        if existing_system_rate:
            data[i]['existing_system_rate'] = existing_system_rate['data']
            data[i]['existing_system_rate']['updated_at'] = existing_system_rate['updated_at']
    
    return data

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

def get_stats(query, filters, page, page_limit, sort_by, sort_type, stats_required):
    if not stats_required:
        return {}
    
    if 'trade_type' in filters:
        del filters['trade_type'] 
    
    if 'status' in filters:
        del filters['status']

    query = FclFreightRateTask.select()

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