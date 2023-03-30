from micro_services.client import organization
from services.fcl_freight_rate.interaction.list_fcl_freight_rates import list_fcl_freight_rates
import concurrent.futures
from database.rails_db import get_eligible_orgs

def list_dashboard_fcl_freight_rates():

    fcl_service_provider_ids = get_eligible_orgs('fcl_freight')
    air_service_provider_ids = get_eligible_orgs('air_freight')
    
    port_pairs = get_port_pairs()

    with concurrent.futures.ThreadPoolExecutor(max_workers = len(port_pairs)) as executor:
        futures = [executor.submit(get_rate, port_pair, fcl_service_provider_ids, air_service_provider_ids) for port_pair in port_pairs if port_pair['service'] == 'fcl_freight']
        lists = []
        for future in futures:
            result = future.result()
            lists.append(result)
    
    lists = list(filter(None, lists))
        
    for rate in lists:
        for validity in rate['validities']:
            try:
                validity['price'] = validity['price'] * 1.2 
                validity['min_price'] = validity['min_price'] * 1.2 
            except:
                validity['price'] = None
                validity['min_price'] = None
            
            if not validity['price']:
                validity['price'] = validity['min_price'] 

    return {'list': lists }


def get_port_pairs():
    return [
    {
    'service': 'fcl_freight',
    'origin_port_id': '6eb66c1b-9348-4fb9-a9e7-37c5d153272e',
    'destination_port_id': 'eb187b38-51b2-4a5e-9f3c-978033ca1ddf'
    },
    {
        'service': 'fcl_freight',
        'origin_port_id': '33470eb3-0a63-4427-bf7e-b68d043364dc',
        'destination_port_id': '3c843f50-867c-4b07-bb57-e61af97dabfe'
    },
    {
        'service': 'fcl_freight',
        'origin_port_id': '2b318074-ad35-41e9-bb00-68d27a47ec47',
        'destination_port_id': '1ae214c1-5deb-4dbd-8f5f-8252abd56950'
    },
    {
        'service': 'fcl_freight',
        'origin_port_id': 'eb187b38-51b2-4a5e-9f3c-978033ca1ddf',
        'destination_port_id': '3a6bcb1f-1367-4c1c-b619-62b815db6089'
    },
    {
        'service': 'air_freight',
        'origin_airport_id': '0d674a4f-2395-4720-80fe-b5fc3847b16a',
        'destination_airport_id': '06b9cf22-74bf-496b-ab6d-8dcb67489233'
    },
    {
        'service': 'air_freight',
        'origin_airport_id': '9cc32c5f-265a-4610-a15b-7f9de8bd3d84',
        'destination_airport_id': '7391cac2-e8db-467f-a59b-574d01dd7e7c'
    },
    {
        'service': 'air_freight',
        'origin_airport_id': '465663fe-166a-4d20-a4ad-e1225b17bc3c',
        'destination_airport_id': 'aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19'
    },
    {
        'service': 'air_freight',
        'origin_airport_id': 'aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19',
        'destination_airport_id': '304d3eeb-69fe-4ecc-9b7f-4f343609e54c'
    }
    ]


def get_rate(port_pair, fcl_service_provider_ids, air_service_provider_ids):
    data = {
    'filters': {
        'is_rate_available': True,
        'service_provider_id': fcl_service_provider_ids if port_pair['service'] == 'fcl_freight' else air_service_provider_ids
    },
    'page': 1, 'page_limit': 1,
    'pagination_data_required': False
    }

    data = data['filters'] | (port_pair)
    response = eval("list_{}_rates(filters = data)".format(port_pair['service']))['list']
    if response:
        response = response[0]
    else:
        response = None
    return response