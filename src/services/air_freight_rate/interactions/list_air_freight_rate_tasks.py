from fastapi import HTTPException
from datetime import datetime,timedelta
from math import ceil
from micro_services.client import common,shipment
from configs.definitions import AIR_FREIGHT_LOCAL_CHARGES
from libs.get_filters import get_filters
from services.air_freight_rate.models.air_freight_rate_tasks import AirFreightRateTasks
from services.air_freight_rate.constants.air_freight_rate_constants import EXPECTED_TAT,DEFAULT_SERVICE_PROVIDER_ID,DEFAULT_PROCURED_BY_ID,DEFAULT_SOURCED_BY_ID
from peewee import *
from configs.global_constants import MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT
from services.air_freight_rate.models.air_freight_rate_local import AirFreightRateLocal
import json
from fastapi.encoders import jsonable_encoder
from libs.get_applicable_filters import get_applicable_filters
from libs.get_filters import get_filters

POSSIBLE_DIRECT_FILTERS = ['airport_id', 'logistics_service_type', 'commodity', 'airline_id', 'trade_type', 'status', 'task_type']
POSSIBLE_INDIRECT_FILTERS = ['updated_at_greater_than', 'updated_at_less_than']

def list_air_freight_rate_tasks(filters={},page_limit=10,page=1,sort_by = 'created_at', sort_type = 'desc', stats_required = True, pagination_data_required = True):
    query = get_query(sort_by, sort_type)
    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)
        direct_filters, indirect_filters = get_applicable_filters(filters, POSSIBLE_DIRECT_FILTERS, POSSIBLE_INDIRECT_FILTERS)
    
        query = get_filters(direct_filters, query, AirFreightRateTasks)
        query = apply_indirect_filters(query, indirect_filters)

    pagination_data=get_pagination_data(query,page,page_limit)

    query=query.paginate(page,page_limit)
    data=get_data(query,filters)
    stats=get_stats(filters,stats_required)
    return{
        'list':jsonable_encoder(data)
    } | (pagination_data) |(stats)

def apply_indirect_filters(query, filters):
    for key in filters:
        if key in POSSIBLE_INDIRECT_FILTERS:
            apply_filter_function = f'apply_{key}_filter'
            query = eval(f'{apply_filter_function}(query, filters)')
    return query 

def apply_updated_at_greater_than_filter(query,filters):
    query = query.where(AirFreightRateTasks.updated_at.cast('date') >= datetime.strptime(filters['updated_at_greater_than'], '%Y-%m-%dT%H:%M:%S.%f%z').date())
    return query

def apply_updated_at_less_than_filter(query,filters):
    query = query.where(AirFreightRateTasks.updated_at.cast('date') <= datetime.strptime(filters['updated_at_less_than'], '%Y-%m-%dT%H:%M:%S.%f%z').date())
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

def get_existing_system_rates(airport_ids,commodities,trade_types,airline_ids,commodity_types):
    existing_system_rates = AirFreightRateLocal.select().where(
        AirFreightRateLocal.airport_id << airport_ids,
        AirFreightRateLocal.commodity << commodities,
        AirFreightRateLocal.commodity_type << commodity_types,
        AirFreightRateLocal.trade_type << trade_types,
        AirFreightRateLocal.airline_id << airline_ids,
        AirFreightRateLocal.service_provider_id == DEFAULT_SERVICE_PROVIDER_ID

    )

    return jsonable_encoder(list(existing_system_rates.dicts()))

def get_shipment_and_sell_quotations(all_shipment_serial_ids):
    shipments = shipment.list_shipments({'filters': { 'serial_id': all_shipment_serial_ids},'page_limit':1000})
    shipment_ids = []
    shipment_dict = {}
    for shipment_data in shipments:
        if shipment_data['serial_id'] in shipment_data.keys():
            shipment_dict[shipment_data['serial_id'] ] = shipment_dict[shipment_data['serial_id']] + [shipment_data]
        else:
            shipment_dict[shipment_data['serial_id'] ] = [shipment_data]
        shipment_ids.append(shipment_data['id'])
    
    shipment_sell_quotation_dict = {}
    quotations = shipment.list_shipment_sell_quotations({'filters':{'shipment_id':shipment_ids,'service_type': 'air_freight_local_service', 'is_deleted': False, 'source': 'billed_at_actuals'},'page_limit':MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT })
    for quotation in quotations:
        if quotation['shipment_id'] in shipment_sell_quotation_dict:
            shipment_sell_quotation_dict[quotation['shipment_id']] = shipment_sell_quotation_dict[quotation['shipment_id']] + [quotation]
        else:
            shipment_sell_quotation_dict[quotation['shipment_id']] = [quotation]
    
    return shipment_dict,shipment_sell_quotation_dict
                                    
def get_data(query,filters):
    new_data=[]
    air_freight_local_charges = AIR_FREIGHT_LOCAL_CHARGES

    data_list = jsonable_encoder(list(query.dicts()))
    airport_ids = []
    commodities = []
    trade_types = []
    airline_ids = []
    commodity_types = []

    all_shipment_serial_ids =[]
    for data in data_list:
        if data['airport_id']:
            airport_ids.append(data['airport_id'])
        if data['commodity']:
            commodities.append(data['commodity'])
        if data['trade_type']:
            trade_types.append(data['trade_type'])
        if data['commodity_type']:
            commodity_types.append(data['commodity_type'])
        if data['airline_id']:
            airline_ids.append(data['airline_id'])

        if data['shipment_serial_ids']:
            all_shipment_serial_ids.extend(data['shipment_serial_ids'])
    
    all_shipment_serial_ids = list(set(all_shipment_serial_ids))
    if all_shipment_serial_ids:
        shipments_dict,shipment_quotation_dict = get_shipment_and_sell_quotations(all_shipment_serial_ids)

    existing_system_rates = get_existing_system_rates(airport_ids,commodities,trade_types,airline_ids,commodity_types)
    for object in data_list:

        if filters['status']== object['status']:
            if object['status'] != 'completed':
                created_at_date = datetime.fromisoformat(object['created_at']).date()
                next_date = datetime.fromisoformat(object['created_at']).date()+ timedelta(days = 1)

                object['expiration_time'] = datetime.fromisoformat(object['created_at']) + timedelta(seconds = EXPECTED_TAT * 60 * 60)
                object['skipped_time'] = 0

                if datetime.fromisoformat(object['created_at']) < datetime.strptime("{} 04:00:00".format(str(created_at_date)), '%Y-%m-%d %H:%M:%S'):
                    object['expiration_time'] = datetime.strptime("{} 04:00:00".format(str(created_at_date)), '%Y-%m-%d %H:%M:%S') + timedelta(seconds = EXPECTED_TAT * 60 * 60)
                elif datetime.fromisoformat(object['created_at']) > datetime.strptime("{} 13:00:00".format(str(created_at_date)), '%Y-%m-%d %H:%M:%S'):
                    object['expiration_time'] = datetime.strptime("{} 04:00:00".format(str(next_date)), '%Y-%m-%d %H:%M:%S') + timedelta(seconds = EXPECTED_TAT * 60 * 60)
                else:
                    skipped_time = int((datetime.fromisoformat(object['created_at']) + timedelta(seconds = EXPECTED_TAT * 60 * 60)).timestamp()) - int(datetime.strptime("{} 13:00:00".format(str(created_at_date)), '%Y-%m-%d %H:%M:%S').timestamp())
                    skipped_time = max([0, skipped_time])
                    if skipped_time > 0:
                        object['expiration_time'] = datetime.strptime("{} 04:00:00".format(str(next_date.date())), '%Y-%m-%d %H:%M:%S') + timedelta(seconds = skipped_time)

                
                object['closable'] = False
                serial_ids = []
                if object.get('shipment_serial_ids'):
                    for serial_id in object.get('shipment_serial_ids'):
                        for shipment in shipments_dict[serial_id]:
                            if shipment['state'] in ['cancelled', 'aborted']:
                                serial_ids.append(serial_id)
                                break
                            for quotation in shipment_quotation_dict[shipment['id']]:
                                if quotation['line_item']:
                                    serial_ids.append(serial_id)
                                    break
                    
                    if len(set(object.get('shipment_serial_ids')).difference(set(serial_ids))):
                        object['closable'] = True
                object['purchase_invoice_rate'] = object['job_data']['rate']
                del object['job_data']


            if filters and 'status' in filters and filters['status'] == 'completed':
                rate = object['completion_data'].get('rate')

                rate['total_price'] = 0
                rate['total_price_currency'] = rate['line_items'][0]['currency'] or 'INR'
                
                for line_item in rate['line_items']:
                    line_item['name'] = air_freight_local_charges[line_item['code']]['name']
                    if line_item['currency']!=rate['total_price_currency']:
                        rate['total_price'] += common.get_money_exchange_for_fcl({'from_currency': line_item['currency'], 'to_currency': rate['total_price_currency'], 'price': line_item['price']})['price']
                    else:
                        rate['total_price'] = line_item['price']
                object['rate'] = rate

                object['expiration_time'] = datetime.fromisoformat(object['created_at']) + timedelta(hours = 6)

                object['completion_time'] = int(datetime.fromisoformat(object['completed_at']).timestamp()) - int(datetime.fromisoformat(object['created_at']).timestamp())

                object['completed_at'] = str(datetime.fromisoformat(object['completed_at']))
                if object['completion_time'] < (0.5 * 60 * 60):
                    object['remark'] = 'Super Fast' 
                if object['completion_time'] > (0.5 * 60 * 60) and object['completion_time'] <= (EXPECTED_TAT * 60 * 60):
                    object['remark'] = 'On Time' 
                if object['completion_time'] > (EXPECTED_TAT * 60 * 60):
                    object['remark'] = 'Delayed' 

                del object['completion_data']
            
            object['service_provider_id'] = DEFAULT_SERVICE_PROVIDER_ID
            object['sourced_by_id'] = DEFAULT_SOURCED_BY_ID
            object['procured_by_id'] = DEFAULT_PROCURED_BY_ID
            object['existing_system_rate'] = {}
            existing_system_rate = get_matching_rate(existing_system_rates,object)
            if existing_system_rate:
                object['existing_system_rate']['line_items'] = existing_system_rate['line_items']
                object['existing_system_rate']['updated_at'] = existing_system_rate['updated_at']
            new_data.append(object)
    return new_data

def get_matching_rate(existing_system_rates,object):
    for rate in existing_system_rates:
        if object['airport_id'] == rate['airport_id'] and object['commodity'] == rate['commodity'] and object['commodity_type'] == rate['commodity_type'] and object['trade_type'] == rate['trade_type'] and object['airline_id'] == rate['airline_id']:
            return rate
    
    return None
def get_stats(filters,stats_required):
    if not stats_required:
        return {}

    query = AirFreightRateTasks.select()

    if filters:
        if 'trade_type' in filters:
            del filters['trade_type'] 
        
        if 'status' in filters:
            del filters['status']

        direct_filters, indirect_filters = get_applicable_filters(filters, POSSIBLE_DIRECT_FILTERS, POSSIBLE_INDIRECT_FILTERS)
  
        query = get_filters(direct_filters, query, AirFreightRateTasks)
        query = apply_indirect_filters(query, indirect_filters)
    
    query = query.select(fn.COUNT(SQL('*')).alias('count_all'), AirFreightRateTasks.status.alias('air_freight_task_status'), AirFreightRateTasks.trade_type.alias('air_freight_task_trade_type')).group_by(AirFreightRateTasks.status, AirFreightRateTasks.trade_type)
    query_result = {}
    for i in query.execute():
        lists = [i.air_freight_task_status,i.air_freight_task_trade_type]
        query_result[tuple(lists)] = i.count_all

    stats = { 'pending': { 'export': 0, 'import': 0, 'total': 0 }, 'completed': { 'export': 0, 'import': 0, 'total': 0 }, 'aborted': { 'export': 0, 'import': 0, 'total': 0 } }
     
    for result in query.execute():
        status = result.air_freight_task_status
        trade_type = result.air_freight_task_trade_type
        count = result.count_all
        stats[status][trade_type] += count
        stats[status]['total'] += count

    return {
        'stats': stats
    }
def get_query(sort_by,sort_type):
    query = AirFreightRateTasks.select().order_by(eval('AirFreightRateTasks.{}.{}()'.format(sort_by, sort_type)))
    return query
