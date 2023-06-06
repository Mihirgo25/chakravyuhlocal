from fastapi import HTTPException
from datetime import datetime,timedelta
from math import ceil
from micro_services.client import common
from configs.definitions import AIR_FREIGHT_LOCAL_CHARGES
from libs.get_filters import get_filters
from services.air_freight_rate.models.air_freight_rate_tasks import AirFreightRateTasks
from configs.air_freight_rate_constants import EXPECTED_TAT
from libs.json_encoder import json_encoder
from peewee import *

POSSIBLE_DIRECT_FILTERS = ['airport_id', 'logistics_service_type', 'commodity', 'airline_id', 'trade_type', 'status', 'task_type']
POSSIBLE_INDIRECT_FILTERS = ['updated_at_greater_than', 'updated_at_less_than']

def list_air_freight_rate_tasks(filters={},page_limit=10,page=1,sort_by = 'created_at', sort_type = 'desc', stats_required = True, pagination_data_required = True):
    query = get_query(sort_by, sort_type)
    filters = {k for k,v  in filters.items() if v is not None}
    unexpected_filters = set(filters.keys()) - (set(POSSIBLE_DIRECT_FILTERS) | set(POSSIBLE_INDIRECT_FILTERS))
    filters = {k for k in filters.items() if k not in unexpected_filters}

    query=get_filters(POSSIBLE_DIRECT_FILTERS,query,AirFreightRateTasks)
    query=apply_indirect_filters(query,filters)

    pagination_data=get_pagination_data(query,page,page_limit)
    query=query.paginate(page,page_limit)
    data=get_data(query,filters)

    stats=get_stats(filters)

    return{
        'list':json_encoder(data)
    } | (pagination_data) |(stats)

def apply_indirect_filters(query, filters):
    for key in filters:
        if key in POSSIBLE_INDIRECT_FILTERS:
            apply_filter_function = f'apply_{key}_filter'
            query = eval(f'{apply_filter_function}(query, filters)')
    return query 
def get_pagination_data(query,page,page_limit):
    total_count=query.count()
    params={
      'page': page,
      'total': ceil(total_count/page_limit),
      'total_count': total_count,
      'page_limit': page_limit

    }
    return params

def get_data(query,filters):
    new_data=[]
    air_freight_local_charges = AIR_FREIGHT_LOCAL_CHARGES
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

        if filters and 'status' in filters and filters['status'] == 'completed':
            rate = object['completion_data'].get('rate')

            rate['total_price'] = 0
            rate['total_price_currency'] = rate['line_items'][0]['currency'] or 'INR'
            
            for i in range(len(rate['line_items'])):
                rate['line_items'][i]['name'] = air_freight_local_charges[rate['line_items'][i]['code']]['name']
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
        new_data.append(object)
    return new_data

def get_stats(filters):

    query = AirFreightRateTasks.select()

    if filters:
        if 'trade_type' in filters:
            del filters['trade_type'] 
        
        if 'status' in filters:
            del filters['status']

        # direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)
  
        query = get_filters(POSSIBLE_DIRECT_FILTERS, query, AirFreightRateTasks)
        query = apply_indirect_filters(query, POSSIBLE_INDIRECT_FILTERS)
    
    query = query.select(fn.COUNT(SQL('*')).alias('count_all'), AirFreightRateTasks.status.alias('fcl_freight_task_status'), AirFreightRateTasks.trade_type.alias('fcl_freight_task_trade_type')).group_by(AirFreightRateTasks.status, AirFreightRateTasks.trade_type)
    query_result = {}
    for i in query.execute():
        lists = [i.air_freight_task_status,i.air_freight_task_trade_type]
        query_result[tuple(lists)] = i.count_all

    stats = { 'pending': { 'export': 0, 'import': 0, 'total': 0 }, 'completed': { 'export': 0, 'import': 0, 'total': 0 }, 'aborted': { 'export': 0, 'import': 0, 'total': 0 } }
     
    for stat,count in query_result.items():
        stats[stat[0]][stat[1]] += count
        stats[stat[0]]['total'] += count

    return {
        'stats': stats
    }
def get_query(sort_type,sort_by):
    query = AirFreightRateTasks.select().order_by(eval('AirFreightRateTasks.{}.{}()'.format(sort_by, sort_type)))
    return query
