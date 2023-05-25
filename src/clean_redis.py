from database.db_session import rd
from services.chakravyuh.models.fcl_freight_rate_estimation import FclFreightRateEstimation
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from fastapi.encoders import jsonable_encoder
from micro_services.client import maps
from services.fcl_freight_rate.helpers.get_multiple_service_objects import get_multiple_service_objects
# from celery_worker import delete_fcl_freight_rates_delay
from services.fcl_freight_rate.interaction.delete_fcl_freight_rate import delete_fcl_freight_rate
from configs.definitions import ROOT_DIR
import os
import pandas as pd
from math import ceil
from datetime import datetime
from database.rails_db import get_ff_mlo
from services.fcl_freight_rate.models.fcl_freight_rate_local import FclFreightRateLocal
from services.fcl_freight_rate.interaction.delete_fcl_freight_rate_local import delete_fcl_freight_rate_local
from joblib import Parallel, delayed

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

    for object in rates_to_update.iterator():
        delay_func(object)
    print('Done')


def update_transformation_objects():
    origins = FclFreightRateEstimation.select(FclFreightRateEstimation.origin_location_id.distinct()).where(FclFreightRateEstimation.origin_location.is_null(True), FclFreightRateEstimation.status == 'active')
    destinatons = FclFreightRateEstimation.select(FclFreightRateEstimation.destination_location_id.distinct()).where(FclFreightRateEstimation.destination_location.is_null(True), FclFreightRateEstimation.status == 'active')
    limit_size = 50
    origin_count = 0
    while True:
        rates = origins.limit(limit_size)
        if not rates.exists():
            break

        estimations = jsonable_encoder(list(rates.dicts()))
        location_ids = []

        for estimation in estimations:
            location_ids.append(estimation['origin_location_id'])
        
        locations_list = maps.list_locations({ 'filters': { 'id': location_ids }, 'page_limit': 50 })

        if 'list' in locations_list:
            locations = locations_list['list']
            for location in locations:
                FclFreightRateEstimation.update(origin_location=location).where(
                    FclFreightRateEstimation.origin_location_id == location['id']
                ).execute()
        
        origin_count = origin_count + 1
        print('O', origin_count)
    
    destination_count = 0
    while True:
        rates = destinatons.limit(limit_size)
        if not rates.exists():
            break

        estimations = jsonable_encoder(list(rates.dicts()))
        location_ids = []

        for estimation in estimations:
            location_ids.append(estimation['destination_location_id'])
        
        locations_list = maps.list_locations({ 'filters': { 'id': location_ids }, 'page_limit': 50 })

        print(location_ids)

        if 'list' in locations_list:
            locations = locations_list['list']
            for location in locations:
                FclFreightRateEstimation.update(destination_location=location).where(
                    FclFreightRateEstimation.destination_location_id == location['id']
                ).execute()
        
        destination_count = destination_count + 1
        print('D', destination_count)


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
            
def delete_fcl_locals():
    file_path = os.path.join(ROOT_DIR, 'Wrong Locals.xlsx')
    ids = pd.read_excel(file_path)['id'].to_list()
    ids = list(set(ids))
    for idx, id in enumerate(ids):
        obj = {
            "id": str(id),
            "performed_by_id": "15cd96ec-70e7-48f4-a4f9-57859c340ee7",
            "sourced_by_id": "15cd96ec-70e7-48f4-a4f9-57859c340ee7",
            "procured_by_id": "15cd96ec-70e7-48f4-a4f9-57859c340ee7",
            "performed_by_type": "agent"
        }
        delete_fcl_freight_rate_local(obj)
        print(idx, id)
        
def extend_china_rates():
    file_path = os.path.join(ROOT_DIR, 'CHINA Cogoenvision.xlsx')
    df = pd.read_excel(file_path)
    print(df.shape[0])
    result = Parallel(n_jobs=2)(delayed(create_func)(idx, row) for idx, row in df.iterrows())
    print(len(result))
        
        
def create_func(idx, row):
    from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
    from services.fcl_freight_rate.models.fcl_freight_rate_audit import FclFreightRateAudit
    id = str(row['rate_id'])
    price = float(row['price'])
    rate = FclFreightRate.select().where(FclFreightRate.id == id).first()
    if not rate:
        print('not_found')
        return
    create_rate = True
    validities = rate.validities
    validity_end = validities[-1]['validity_end']
    for validity in validities:
        validity['validity_start'] = '2023-05-25'
        if validity['validity_start'] >= validity['validity_end']:
            print('__|__')
            create_rate = False
            continue
        for item in validity['line_items']:
            if item['code'] == 'BAS':
                item['price'] = price
                validity['price'] = price
                validity['platform_price'] = price
    
    if not create_rate:
        return
                
    rate.validities = validities
    rate.save()
    rate.set_platform_prices()
    
    data = {
        'validity_end': validity_end,
        'validity_start': '2023-05-25',
        'line_items': validities[-1]['line_items'],
        'weight_limit': rate.weight_limit,
        'origin_local': rate.origin_local,
        'destination_local': rate.destination_local,
        'source': 'rate_extension'
    }

    id = FclFreightRateAudit.create(
        action_name="create",
        performed_by_id='15cd96ec-70e7-48f4-a4f9-57859c340ee7',
        data=data,
        object_id=id,
        object_type="FclFreightRate",
        source='rate_extension',
    )
    print(idx)
    
        
        
    
