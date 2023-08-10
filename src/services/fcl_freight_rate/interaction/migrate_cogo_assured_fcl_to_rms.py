import pickle
from configs.definitions import ROOT_DIR
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
import json
import os
from micro_services.client import maps
from uuid import UUID
from configs.fcl_freight_rate_constants import DEFAULT_PAYMENT_TERM, DEFAULT_SCHEDULE_TYPES
from services.fcl_freight_rate.models.fcl_freight_rate_properties import FclFreightRateProperties
from database.rails_db import get_connection
import sentry_sdk
import datetime
from configs.env import DEFAULT_USER_ID
from fastapi.encoders import jsonable_encoder
from services.fcl_freight_rate.models.fcl_freight_rate_local import FclFreightRateLocal


shipping_line = {
    'id': 'e6da6a42-cc37-4df2-880a-525d81251547',
    'status': 'active',
    'logo_url': 'https://cogoport-production.sgp1.digitaloceanspaces.com/a415fa5daceb33172e0319bbd3357c96/cogo-line.png',
    'short_name': 'COGO LINE',
    'operator_type': 'shipping_line'
}

service_provider = {
    'id': '5dc403b3-c1bd-4871-b8bd-35543aaadb36',
    'status': 'active',
    'kyc_status': 'verified',
    'short_name': 'Cogoport',
    'account_type': 'service_provider',
    'business_name': 'COGO FREIGHT PRIVATE LIMITED',
    'category_types': ['internal']
}

user = {
    'id': '2dbe768e-929d-4e54-baf0-309ef68c978b',
    'name': 'Cogo Envision',
    'email': 'cogo.envision@cogoport.com',
    'mobile_number_eformat': '919649665944'
}

def cogo_assured_fcl_freight_migration():
    fcl_audits_path = os.path.join(ROOT_DIR,"cogo_assured_rate_lists.pkl")
    fcl_rates = pickle.load(open(fcl_audits_path, 'rb'))
    rates_to_insert = []
    total_inserted = 0
    count = 0
    for rate in fcl_rates:
        count = count + 1
        rate["container_size"] = str(rate["container_size"])
        rate['origin_location_ids'] = [UUID(rate['origin_port_id']), UUID(rate['origin_country_id']), UUID(rate['origin_trade_id']), UUID(rate['origin_continent_id'])]
        rate['destination_location_ids'] = [UUID(rate['destination_port_id']), UUID(rate['destination_country_id']), UUID(rate['destination_trade_id']), UUID(rate['destination_continent_id'])]
        rate['validities'] = json.loads(rate['validities'])
        for validity in rate["validities"]:
            validity["payment_term"] = DEFAULT_PAYMENT_TERM
            validity['scehdule_type'] = DEFAULT_SCHEDULE_TYPES
            validity["likes_count"] = 0
            validity["dislikes_count"] = 0
        rate['weight_limit'] = json.loads(rate.get('weight_limit')) if rate.get('weight_limit') else None
        rate['origin_local'] = json.loads(rate.get('origin_local')) if rate.get('origin_local') else None
        rate['destination_local'] = json.loads(rate.get('destination_local')) if rate.get('destination_local') else None
        rate['destination_local_line_items_error_messages'] = json.loads(rate.get('destination_local_line_items_error_messages')) if rate.get('destination_local_line_items_error_messages') else None
        rate['destination_local_line_items_info_messages'] = json.loads(rate.get('destination_local_line_items_info_messages')) if rate.get('destination_local_line_items_info_messages') else None
        rate['origin_local_line_items_error_messages'] = json.loads(rate.get('origin_local_line_items_error_messages')) if rate.get('origin_local_line_items_error_messages') else None
        rate['origin_local_line_items_info_messages'] = json.loads(rate.get('origin_local_line_items_info_messages')) if rate.get('origin_local_line_items_info_messages') else None
        rate['rate_type'] = 'cogo_assured'
        if rate['container_size'] == "40":
            rate_copy = rate.copy()
            rate_copy["container_size"] = "40HC"
            rates_to_insert.append(rate_copy)
        
        rates_to_insert.append(rate)
        if len(rates_to_insert) > 10000:
            print('Yes')
            total_inserted = total_inserted + len(rates_to_insert)
            FclFreightRate.insert_many(rates_to_insert).execute()
            rates_to_insert = []
            print('Inserted', total_inserted)
    FclFreightRate.insert_many(rates_to_insert).execute()
    print('Done')
    
def migrate_rate_properties():
    cogo_assured_ids = (FclFreightRate.select(FclFreightRate.id).where(FclFreightRate.rate_type == 'cogo_assured'))
    properties = []
    for id in cogo_assured_ids.execute():
        properties.append({
            "rate_id": id.id
        })
    FclFreightRateProperties.insert_many(properties).execute()
    
    
def cogo_assured_fcl_freight_local_migration():
    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cur:
                query = 'select cogo_assured_fcl_freight_local_rates.container_size,cogo_assured_fcl_freight_local_rates.container_type,cogo_assured_fcl_freight_local_rates.commodity,cogo_assured_fcl_freight_local_rates.service_provider_id,cogo_assured_fcl_freight_local_rates.shipping_line_id,cogo_assured_fcl_freight_local_rates.validity_start,cogo_assured_fcl_freight_local_rates.validity_end,cogo_assured_fcl_freight_local_rates.price,cogo_assured_fcl_freight_local_rates.currency,cogo_assured_rates.location_id, cogo_assured_rates.port_id, cogo_assured_rates.country_id, cogo_assured_rates.trade_id, cogo_assured_rates.continent_id,cogo_assured_rates.trade_type from cogo_assured_fcl_freight_local_rates join cogo_assured_rates on cogo_assured_fcl_freight_local_rates.cogo_assured_rate_id = cogo_assured_rates.id where cogo_assured_rates.primary_service = %s and cogo_assured_fcl_freight_local_rates.status = %s'
                cur.execute(query, ('fcl_freight_local', 'active'))
                local_rates = jsonable_encoder(cur.fetchall())
                count = 0
                row_data = []
                distinct_port_ids = []
                for rate in local_rates:
                    count+= 1
                    print(count)
                    data = {}
                    data['line_items'] = [{
                        'code': 'THC',
                        'unit': "per_container",
                        'price':rate[7] ,
                        'currency':rate[8],
                        'validity_start': rate[5],
                        'validity_end':rate[6],
                        "slabs": [],
                        "remarks": [],
                        "location_id": None 
                    }]

                    result = {
                        'container_size' : rate[0],
                        'container_type' : rate[1],
                        'commodity' : rate[2],
                        'service_provider_id' : service_provider['id'],
                        'service_provider': service_provider,
                        'shipping_line_id' : shipping_line['id'],
                        'shipping_line':shipping_line,
                        'port_id' : rate[9],
                        'main_port_id' : rate[10],
                        'country_id': rate[11],
                        'trade_id' : rate[12],
                        'continent_id' : rate[13],
                        'trade_type' : rate[14],
                        'rate_type':'cogo_assured',
                        'procured_by_id': DEFAULT_USER_ID,
                        'sourced_by_id': DEFAULT_USER_ID,
                        'sourced_by': user,
                        'procured_by': user,
                        'data': data,
                        'line_items': data['line_items']
                    }
                    if not rate[9] in distinct_port_ids:
                        distinct_port_ids.append(rate[9])
                    if not rate[10] in distinct_port_ids:
                        distinct_port_ids.append(rate[10])
                    row_data.append(result)
                cur.close()
                FclFreightRateLocal.insert_many(row_data).execute()
                update_locations(distinct_port_ids)
        conn.close()
        return {"message": "Created rates in fcl with tag cogo_assured"}
    except Exception as e:
        print('failed')
        print(e)
        
def update_locations(distinct_port_ids):
    locations_list = maps.list_locations({ 'filters': { 'id': distinct_port_ids }, 'page_limit': len(distinct_port_ids)})
    
    if 'list' in locations_list:
        locations = locations_list['list']
        for location in locations:
            FclFreightRateLocal.update(port=location).where(
                (FclFreightRateLocal.port_id == location['id']) & (FclFreightRateLocal.rate_type == 'cogo_assured')
            ).execute()
            
            FclFreightRateLocal.update(main_port=location).where(
                (FclFreightRateLocal.main_port == location['id']) & (FclFreightRateLocal.rate_type == 'cogo_assured')
            ).execute()
            
            
            
    

if __name__ == "__main__":
    cogo_assured_fcl_freight_local_migration()
