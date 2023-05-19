from celery_worker import fcl_freight_rates_local_creation_in_delay
from configs.global_constants import HAZ_CLASSES
from configs.fcl_freight_rate_constants import DEFAULT_SERVICE_PROVIDER_ID, DEFAULT_SHIPPING_LINE_ID
from rms_utils.get_in_batches import get_in_batches
from services.fcl_freight_rate.models.fcl_freight_rate_local import FclFreightRateLocal
from micro_services.client import maps
from configs.definitions import ROOT_DIR
import pandas as pd, os
import copy

def get_local_rates_from_vyuh(local_rate_param, line_items = []):
    ports_data = get_locations(local_rate_param.get('country_id'))
    icd_ports, combined_ids = [], []
    for data in ports_data:
        if data.get('is_icd') == True:
            icd_ports.append(str(data.get('id')))
        elif data.get('is_icd') == False:
            combined_ids.append(str(data.get('id')) + ':')

    main_ports_icd_mapping = maps.list_locations_mapping({'location_id':icd_ports,'type':['main_ports']})
    if isinstance(main_ports_icd_mapping, dict) and main_ports_icd_mapping.get('list'):
        main_ports_data = main_ports_icd_mapping['list']
    else:
        main_ports_data = []

    for port in main_ports_data:
        combined_ids.append(str(port['icd_port_id'])+':'+str(port['id']))

    query_result = get_search_query(local_rate_param)
    mapping_from_query = [str(row['port_id'])+':'+str(row['main_port_id'] or '') for row in query_result]
    final_list = list(set(combined_ids).difference(set(mapping_from_query)))
    
    if final_list:
        local_rates = create_fcl_freight_local_in_delay(local_rate_param, line_items, final_list)
    else:
        local_rates = []
    return local_rates

def get_locations(location_id):
    locations = maps.list_locations({'filters':{'country_id': location_id, 'status':'active', "type":"seaport" },'page_limit':10000})
    if isinstance(locations, dict) and locations.get('list'):
        return locations['list']
    else:
        return []

def create_fcl_freight_local_in_delay(param, line_items, final_list):
    final_params = []

    if len(line_items) == 0:
        line_items = get_line_items_from_sheet(param)

    if len(line_items) > 0:
        return_params = []
        local_freight_param = {
        'trade_type':param.get('trade_type'), 
        'main_port_id':param.get('main_port_id'),
        'container_size': param.get('container_size'),
        'container_type': param.get('container_type'),
        'commodity': param.get('commodity') if param.get('commodity') in HAZ_CLASSES else None,
        'service_provider_id': DEFAULT_SERVICE_PROVIDER_ID,
        'source':'predicted',
        'shipping_line_id' : param.get('shipping_line_id') if param.get('shipping_line_id') else DEFAULT_SHIPPING_LINE_ID,
        'performed_by_id':'4ed1f0e6-17c6-4058-9610-bf59657398bd'
        }

        for port in final_list:
            port_id, main_port_id = port.split(':')
            creation_param = local_freight_param | {'port_id': port_id, 'source':'predicted','data':{'line_items':line_items, 'plugin':None, 'detention':None, 'demurrage':None}}
            if main_port_id:
                creation_param['main_port_id'] = main_port_id
            else:
                creation_param['main_port_id'] = None
            if port_id == param.get('port_id'):
                return_params.append(creation_param)
            final_params.append(creation_param)
        # fcl_freight_rates_local_creation_in_delay.apply_async(kwargs={'local_rate_params':final_params}, queue = 'critical')
        return return_params
    else:
        return []

def get_line_items_from_sheet(param):
    FILE_PATH = os.path.join(ROOT_DIR, "services", "chakravyuh", "std_local_updt_3.csv")
    estimated_rates = pd.read_csv(FILE_PATH)
    commodity = param.get('commodity') if param.get('commodity') in HAZ_CLASSES else 'None'
    container_size = param.get('container_size')
    if container_size == '40HC':
        container_size = '40'

    estimated_rates['commodity'].fillna('None', inplace = True)
    line_items = estimated_rates[(estimated_rates.location_id == param.get('country_id')) & (estimated_rates.container_type == param.get('container_type')) & (estimated_rates.container_size == int(container_size)) & (estimated_rates.trade_type == param.get('trade_type')) & (estimated_rates.commodity == commodity)]['line_items']
    if len(line_items) > 0:
        return set_local_line_items(line_items.iloc[0])
    return [] 

def get_search_query(local_rate_param):
    query = FclFreightRateLocal.select().where(
    FclFreightRateLocal.country_id == local_rate_param.get('country_id'),
    FclFreightRateLocal.trade_type == local_rate_param.get('trade_type'),
    FclFreightRateLocal.container_size == local_rate_param.get('container_size'),
    FclFreightRateLocal.container_type == local_rate_param.get("container_type"),
    ((FclFreightRateLocal.commodity == local_rate_param.get('commodity')) | (FclFreightRateLocal.commodity.is_null(True)))
    )

    if local_rate_param.get('shipping_line_id'):
        query = query.where(FclFreightRateLocal.shipping_line_id == local_rate_param['shipping_line_id'])
    return list(query.dicts())

def set_local_line_items(local_rate):
    line_items = []
    rate = copy.deepcopy(eval(local_rate))
    for line_item in rate:
        local_price = round((line_item['upper_price'] + line_item['lower_price'])/2)
        if local_price > 0 and (local_price%10 != 0):
            line_item['price'] = local_price + (5 - local_price%10) if local_price%10 <= 5 else (local_price + (10 - local_price%10))
        else:
            line_item['price'] = local_price
        del line_item['upper_price']
        del line_item['lower_price']
        line_items.append(line_item)
    return line_items