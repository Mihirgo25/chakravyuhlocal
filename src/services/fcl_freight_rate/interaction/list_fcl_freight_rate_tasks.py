from services.fcl_freight_rate.models.fcl_freight_rate_task import FclFreightRateTask
from services.fcl_freight_rate.models.fcl_freight_rate_local import FclFreightRateLocal
from libs.get_filters import get_filters
from libs.get_applicable_filters import get_applicable_filters
from fastapi.encoders import jsonable_encoder
from configs.fcl_freight_rate_constants import *
from playhouse.shortcuts import model_to_dict
from configs.fcl_freight_rate_constants import EXPECTED_TAT
from math import ceil
from configs.definitions import FCL_FREIGHT_LOCAL_CHARGES
from peewee import fn
from datetime import datetime, timedelta
import json
from peewee import SQL
from micro_services.client import common

possible_direct_filters = ['port_id', 'container_size', 'container_type', 'commodity', 'shipping_line_id', 'trade_type', 'status', 'task_type']
possible_indirect_filters = ['created_at_greater_than', 'created_at_less_than']

def list_fcl_freight_rate_tasks(filters = {}, page_limit = 10, page = 1, sort_by = 'created_at', sort_type = 'desc', stats_required = True, pagination_data_required = True):
    query = get_query(sort_by, sort_type)

    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)

        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)
  
        query = get_filters(direct_filters, query, FclFreightRateTask)
        query = apply_indirect_filters(query, indirect_filters)
    
    pagination_data = get_pagination_data(query, page, page_limit, pagination_data_required)
    query = query.paginate(page, page_limit)
    data = get_data(query, filters)
    
    stats = get_stats(filters, stats_required)

    return {'list': data } | (pagination_data) | (stats)
  

def get_query(sort_by, sort_type):
    query = FclFreightRateTask.select().order_by(eval('FclFreightRateTask.{}.{}()'.format(sort_by, sort_type)))
    return query
  
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

def get_data(query, filters):
    new_data = []
    port_ids, main_port_ids, container_sizes, container_types, commodities, trade_types, shipping_line_ids = [],[], [],[], [],[], []
    data_list = list(query.dicts())

    for object in data_list:
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
        if object['main_port_id']:
            main_port_ids.append(object['main_port_id']) 
        
        if object['commodity']:
            commodities.append(object['commodity'])
            
        container_sizes.append(object['container_size']) 
        container_types.append(object['container_type'])
        trade_types.append(object['trade_type']) 
        shipping_line_ids.append(object['shipping_line_id'])
        new_data.append(object)

    if filters and 'status' in filters and filters['status'] == 'completed':
        fcl_freight_local_charges = FCL_FREIGHT_LOCAL_CHARGES

        for object in new_data:
            rate = object['completion_data'].get('rate')

            rate['total_price'] = 0
            rate['total_price_currency'] = rate['line_items'][0]['currency'] or 'INR'
            
            for i in range(len(rate['line_items'])):
                rate['line_items'][i]['name'] = fcl_freight_local_charges[rate['line_items'][i]['code']]['name']
                rate['total_price'] += common.get_money_exchange_for_fcl({'from_currency': rate['line_items'][i]['currency'], 'to_currency': rate['total_price_currency'], 'price': rate['line_items'][i]['price']})['price']
            
            rate['total_price'] = round(rate['total_price'])

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
       
    return new_data


def apply_indirect_filters(query, filters):
    for key in filters:
        if key in possible_indirect_filters:
            apply_filter_function = f'apply_{key}_filter'
            query = eval(f'{apply_filter_function}(query, filters)')
    return query  

def apply_created_at_greater_than_filter(query, filters):
    query = query.where(FclFreightRateTask.updated_at.cast('date') >= datetime.strptime(filters['created_at_greater_than'], '%Y-%m-%dT%H:%M:%S.%f%z').date())
    return query

def apply_created_at_less_than_filter(query, filters):
    query = query.where(FclFreightRateTask.updated_at.cast('date') <= datetime.strptime(filters['created_at_less_than'], '%Y-%m-%dT%H:%M:%S.%f%z').date())
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

        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)
  
        query = get_filters(direct_filters, query, FclFreightRateTask)
        query = apply_indirect_filters(query, indirect_filters)
    
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