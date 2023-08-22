

from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from configs.fcl_freight_rate_constants import RATE_ENTITY_MAPPING
from fastapi.encoders import jsonable_encoder
from datetime import datetime,timedelta
from configs.fcl_freight_rate_constants import DEFAULT_SERVICE_PROVIDER_ID
from configs.env import DEFAULT_USER_ID
from services.fcl_freight_rate.interaction.create_fcl_freight_rate import create_fcl_freight_rate_data
import concurrent.futures

def get_near_expired_rates(requirements):
    from services.fcl_freight_rate.interaction.get_fcl_freight_rate_cards import initialize_freight_query,pre_discard_noneligible_rates,all_rates_predicted
    freight_query = initialize_freight_query(requirements,near_expired_rates = True)

    freight_rates = jsonable_encoder(list(freight_query.dicts()))


    freight_rates = pre_discard_noneligible_rates(freight_rates, requirements)


    rates_to_create = get_rates_to_create(freight_rates,requirements)
    if len(rates_to_create)==0:
        return False

 
    with concurrent.futures.ThreadPoolExecutor(max_workers = 4) as executor:
        futures = [executor.submit(create_fcl_freight_rate_data, param) for param in rates_to_create]
    
    return True

def get_rates_to_create(freight_rates,requirements):
    rates_to_create = []
    for freight_rate in freight_rates:
        validities = freight_rate['validities']
        rates_to_create.append(get_create_param(freight_rate,validities[-1]))
    return rates_to_create
                


def get_create_param(freight,validity):
    param = {
    'origin_port_id': freight['origin_port_id'],
    'destination_port_id': freight['destination_port_id'],
    'container_size': freight['container_size'],
    'container_type': freight['container_type'],
    'commodity': freight['commodity'],
    'shipping_line_id' : freight["shipping_line_id"],
    'weight_limit': freight["weight_limit"],
    'service_provider_id' : DEFAULT_SERVICE_PROVIDER_ID,
    'performed_by_id': DEFAULT_USER_ID,
    'procured_by_id': DEFAULT_USER_ID,
    'sourced_by_id': DEFAULT_USER_ID,
    'source': 'rate_extension',
    'mode': 'expired_extension',
    'extended_from_object_id': freight["id"],
    'origin_main_port_id' :freight['origin_main_port_id'],
    'destination_main_port_id' :freight['destination_main_port_id'],
    "validity_start" :datetime.strptime(datetime.now().date().isoformat(),'%Y-%m-%d'),
    "validity_end" : datetime.strptime((datetime.now()+timedelta(days=7)).date().isoformat(),'%Y-%m-%d'),
    "schedule_type" : validity["schedule_type"],
    "payment_term" : validity["payment_term"],
    "line_items" : validity["line_items"]
    }
    return param
