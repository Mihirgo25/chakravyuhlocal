import pandas as pd
from celery_worker import create_fcl_freight_rate_delay
from services.fcl_freight_rate.interaction.create_fcl_freight_rate import create_fcl_freight_rate_data
from datetime import datetime
from configs.global_constants import HAZ_CLASSES
import numpy

def migration():
    df = pd.read_csv('services/final.csv', low_memory=False)
    print('data reading done')
    # df=df[100000:]
    for i in range(100000,len(df)):
        df['origin_local'][i]=eval(df['origin_local'][i])
        df['origin_local'][i]['detention']=eval(df['origin_local'][i]['detention'])
        df['origin_local'][i]['demurrage']=eval(df['origin_local'][i]['demurrage'])
        df['origin_local'][i]['plugin']=eval(df['origin_local'][i]['plugin'])
        df['destination_local'][i]=eval(df['destination_local'][i])
        df['destination_local'][i]['detention']=eval(df['destination_local'][i]['detention'])
        df['destination_local'][i]['demurrage']=eval(df['destination_local'][i]['demurrage'])
        df['destination_local'][i]['plugin']=eval(df['destination_local'][i]['plugin'])
        if i%10000==0:
            print(i)
    for i in range(100000,len(df)):
        request = {
        'container_size':str(df['container_size'][i]),
        'container_type':df['container_type'][i],
        'commodity':df['commodity'][i],
        'service_provider_id':df['service_provider_id'][i],
        'shipping_line_id':df['shipping_line_id'][i],
        'status':df['status'][i],
        'weight_limit':df['weight_limit'][i] if not pd.isna(df['weight_limit'][i]) else None,
        'origin_port_id':df['origin_port_id'][i],
        'destination_port_id':df['destination_port_id'][i],
        'value_props':[{"name": "confirmed_space_and_inventory", "free_limit": None}, {"name": "standard_local_charges", "free_limit": None}, {"name": "fixed_exchange_rate", "free_limit": None}] if len(df['value_props'][i])>10 else [],
        't_n_c':[],
        'origin_main_port_id':df['origin_main_port_id'][i] if not pd.isna(df['origin_main_port_id'][i]) else None,
        'destination_main_port_id':df['destination_main_port_id'][i] if not pd.isna(df['destination_main_port_id'][i]) else None,
        'available_inventory':df['available_inventory'][i],
        'used_inventory':df['used_inventory'][i],
        'rate_type':df['rate_type'][i],
        'origin_local':df['origin_local'][i],
        'destination_local':df['destination_local'][i],
        'performed_by_id':df['performed_by_id'][i],
        'procured_by_id':df['procured_by_id'][i],
        'sourced_by_id':df['sourced_by_id'][i],
        'validity_start': datetime.strptime(df['validity_start'][i], '%Y-%m-%d'),
        'validity_end': datetime.strptime(df['validity_end'][i], '%Y-%m-%d'),
        'line_items':eval(df['line_items'][i]),
        'shipment_count':0,
        'volume_count':0
        }
        print(request)
        if request['container_type'] in ['open_top', 'flat_rack', 'iso_tank'] or request['container_size'] == '45HC':
            request['line_items'].append({
            "code": "SPE",
            "unit": "per_container",
            "price": 0,
            "currency": "USD",
            "remarks": [
            ],
            "slabs": []
            })
    
        if request['commodity'] in HAZ_CLASSES:
            request['line_items'].append({
            "code": "HSC",
            "unit": "per_container",
            "price": 0,
            "currency": "USD",
            "remarks": [
            ],
            "slabs": []
         })
        result = create_fcl_freight_rate_delay.apply_async(kwargs={'request':request},queue='cogo_assured')
        print(result)