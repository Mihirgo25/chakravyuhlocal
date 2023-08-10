import pickle
from configs.definitions import ROOT_DIR
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
import json
import os
from uuid import UUID
from configs.fcl_freight_rate_constants import DEFAULT_PAYMENT_TERM, DEFAULT_SCHEDULE_TYPES
from services.fcl_freight_rate.models.fcl_freight_rate_properties import FclFreightRateProperties

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
    