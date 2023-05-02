from database.db_session import rd
# from to_d import a
from datetime import datetime
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.helpers.get_multiple_service_objects import get_multiple_service_objects
# from celery_worker import delete_fcl_freight_rates_delay
from services.fcl_freight_rate.interaction.delete_fcl_freight_rate import delete_fcl_freight_rate
from configs.definitions import ROOT_DIR
import os
import pandas as pd
from math import ceil
from database.rails_db import get_ff_mlo
from services.fcl_freight_rate.models.fcl_freight_rate_local import FclFreightRateLocal

def clean_full_redis():
    redis_keys = rd.keys('*celery-task-meta*')
    print('Total Keys', len(redis_keys))
    total_non_celery = 0
    for key in redis_keys:
        if not 'celery-task-meta' in key:
            total_non_celery = total_non_celery + 1
    if total_non_celery > 0:
        print('Including non celery keys can not delete')
    else:
        if len(redis_keys) > 0:
            rd.delete(*redis_keys)
            print('Deleted ->', total_non_celery)
        else:
            print('No Delete performed')
            
def fcl_freight_objects_updation():
    rates_to_update = FclFreightRate.select().where(
        FclFreightRate.shipping_line.is_null(True) |
        FclFreightRate.service_provider.is_null(True) |
        FclFreightRate.sourced_by.is_null(True) |
        FclFreightRate.procured_by.is_null(True)
    )
    limit_size = 2000
    count=0
    while True:
        batch = rates_to_update.limit(limit_size)
        if not batch.exists():
            break
        
        for object in batch.execute():
            delay_func(object)
            count += 1
            print(count)
    print('Done')
    
    
def delay_func(object):
    get_multiple_service_objects(object)

def delete_rates():
    delete = False
    file_path = os.path.join(ROOT_DIR, 'Maersk rates to be deleted.xlsx')
    a = pd.read_excel(file_path)['rate_id'].to_list()
    for rate in a:
        obj = {
            "id": str(rate),
            "validity_start": datetime.fromisoformat("2023-04-25"),
            "validity_end": datetime.fromisoformat("2023-05-12"),
            "performed_by_id": "15cd96ec-70e7-48f4-a4f9-57859c340ee7",
            "sourced_by_id": "15cd96ec-70e7-48f4-a4f9-57859c340ee7",
            "procured_by_id": "15cd96ec-70e7-48f4-a4f9-57859c340ee7",
            "performed_by_type": "agent",
            "payment_term": "prepaid"
        }
        print(rate)
        delete_fcl_freight_rate(obj)
        # delete_fcl_freight_rates_delay.apply_async(kwargs={'result':obj},queue='low')
        print('l')  

def rate_extension():
    eligible_sp = get_ff_mlo()
    rates = FclFreightRate.select().where(FclFreightRate.last_rate_available_date == '2023-04-30', FclFreightRate.origin_country_id == '541d1232-58ce-4d64-83d6-556a42209eb7', FclFreightRate.service_provider_id.in_(eligible_sp), ~FclFreightRate.rate_not_available_entry, FclFreightRate.mode == 'manual')
    limit_size = 5000
    count = 0
    while True:
        batch_rates = rates.limit(limit_size)
        if not batch_rates.exists():
            break
        
        for rate in batch_rates.execute():
            validities = rate.validities
            for validity in validities:
                if validity['validity_end'] == '2023-04-30':
                    validity['validity_end'] = '2023-05-31'
                    for item in validity['line_items']:
                        if item['code'] == 'BAS':
                            item['price'] = int(ceil((item['price']*1.07)/10)*10)
            rate.validities = validities               
            rate.last_rate_available_date = '2023-05-31'
            rate.save()
            rate.set_platform_prices()
            count += 1
            print(count)
            
def correct_local():
    rates = FclFreightRateLocal.select().where(FclFreightRateLocal.is_line_items_error_messages_present, ~FclFreightRateLocal.rate_not_available_entry, FclFreightRateLocal.updated_at >= '2023-04-26')
    count = 0
    for rate in rates.execute():
        data = rate.data
        line_items = data['line_items']
        if line_items[0]['location_id'] == '74a37f17-b9d7-4cec-82c4-38a8eda8f914':
            print(rate.id)
            for item in line_items:
                item['location_id'] = None
            data['line_items'] = line_items
            rate.data = data
            rate.is_line_items_error_messages_present = False
            rate.line_items_error_messages = None
            if rate.main_port_id == '74a37f17-b9d7-4cec-82c4-38a8eda8f914':
                rate.main_port_id = None
                rate.main_port = None
            rate.save()
            count += 1
            print(count)

        
        
    
