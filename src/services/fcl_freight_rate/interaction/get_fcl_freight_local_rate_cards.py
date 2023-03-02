from services.fcl_freight_rate.models.fcl_freight_rate_locals import FclFreightRateLocal
from services.fcl_freight_rate.models.fcl_freight_rate_local_agent import FclFreightRateLocalAgent
from configs.global_constants import HAZ_CLASSES,CONFIRMED_INVENTORY, PREDICTED_RATES_SERVICE_PROVIDER_IDS
from configs.fcl_freight_rate_constants import LOCATION_HIERARCHY, DEFAULT_EXPORT_DESTINATION_DETENTION, DEFAULT_IMPORT_DESTINATION_DETENTION, DEFAULT_EXPORT_DESTINATION_DEMURRAGE, DEFAULT_IMPORT_DESTINATION_DEMURRAGE, DEFAULT_LOCAL_AGENT_ID
from services.fcl_freight_rate.interaction.list_fcl_freight_rates import to_dict
from libs.dynamic_constants.fcl_freight_rate_dc import FclFreightRateDc
from playhouse.shortcuts import model_to_dict
import yaml

def get_fcl_freight_local_rate_cards(request):
    request = to_dict(request)
    
    if 'rates' in request and request['rates']:
        list = build_response_list(request['rates'])

        return {'list':list}
    
    local_query = initialize_local_query(request)
    
    query_results = select_fields(local_query)

    list = build_response_list(query_results, request)

    return {'list' : list}


def initialize_local_query(request):
    query = FclFreightRateLocal.select().where(
        FclFreightRateLocal.port_id == request['port_id'], 
        FclFreightRateLocal.container_size == request['container_size'], 
        FclFreightRateLocal.container_type == request['container_type'], 
        FclFreightRateLocal.trade_type == request['trade_type'],
        FclFreightRateLocal.is_line_items_error_messages_present == False,
        FclFreightRateLocal.service_provider_id.in_(list(set(list(filter(None, [get_local_agent_ids(request), request['service_provider_id'],DEFAULT_LOCAL_AGENT_ID]))))))

    if request['commodity'] in HAZ_CLASSES:
        query = query.where(FclFreightRateLocal.commodity == request['commodity'])
    else:
        query = query.where(FclFreightRateLocal.commodity == None)
    
    if request['shipping_line_id']:
        query = query.where(FclFreightRateLocal.shipping_line_id == request['shipping_line_id'])

    return query

def select_fields(local_query):
    local_query = local_query.select(FclFreightRateLocal.service_provider_id,FclFreightRateLocal.main_port_id,FclFreightRateLocal.shipping_line_id,FclFreightRateLocal.data)
    return local_query

def build_response_list(query_results, request):
    response_list = []

    for result in query_results.dicts():
        response_object = build_response_object(result, request)
        if not response_object:
            continue

        response_list.append(response_object)
    return response_list

def build_response_object(result, request):
    response_object = {
      'service_provider_id': str(result['service_provider_id']),
      'main_port_id': str(result['main_port_id']),
      'shipping_line_id': str(result['shipping_line_id']),
      'source': 'predicted' if result['service_provider_id'] in PREDICTED_RATES_SERVICE_PROVIDER_IDS else 'spot_rates',
      'tags': []
    }

    if response_object['service_provider_id'] in CONFIRMED_INVENTORY['service_provider_ids']:
        response_object['tags'].append(CONFIRMED_INVENTORY['tag'])

    if not build_local_line_items(result, response_object, request):
        return None

    if not add_free_days_objects(result, response_object, request):
        return None

    return response_object

def build_local_line_items(result, response_object, request):
    response_object['line_items'] = []

    for line_item in result['data'].get('line_items'):
        if (line_item['location_id']) and (line_item['location_id'] not in [request['port_id'], request['country_id']]):
            continue

        line_item = build_local_line_item_object(line_item, request)

        if not line_item:
            continue

        response_object['line_items'].append(line_item)

    if (len(list(set(request['additional_services']).difference([item['code'] for item in response_object['line_items']])))) > 0:
        return False

    if response_object['line_items']:
        return True   

def build_local_line_item_object(line_item, request):
    with open('/Users/user/Desktop/ocean-rms/src/configs/charges/fcl_freight_local_charges.yml', 'r') as file:
        fcl_freight_local_charges = yaml.safe_load(file)

    code_config = fcl_freight_local_charges[line_item['code']]

    is_additional_service = True if 'additional_service' in code_config.get('tags') else False
    if is_additional_service and (line_item['code'] not in request['additional_services']):
        return None

    is_dpd = True if 'dpd' in code_config.get('tags') else False
    if is_dpd and ('import' in code_config.get('trade_types')) and ( not request['include_destination_dpd']):
        return None

    slab_value = None

    if line_item['slabs']:
        if 'slab_containers_count' in code_config.get('tags'):
            slab_value = request['containers_count']

        if 'slab_cargo_weight_per_container' in code_config.get('tags'):
            slab_value = request['cargo_weight_per_container']

    if slab_value:
        slab = [t for t in line_item['slabs'] if (t['lower_limit'] <= slab_value) and (t['upper_limit'] >= slab_value)][0]
        if slab:
            line_item['price'] = slab['price']
            line_item['currency'] = slab['currency']
 

    line_item = {key: line_item[key] for key in ['code', 'unit', 'price', 'currency', 'remarks']}
    if line_item['unit'] == 'per_container':
        line_item['quantity'] = request['containers_count']
    elif line_item['unit'] == 'per_bl':
        line_item['quantity'] = request['bls_count']
    else:
        line_item['quantity'] = 1
    line_item['total_price'] = line_item['quantity'] * line_item['price']
    line_item['name'] = code_config.get('name')
    line_item['is_dpd'] = is_dpd if is_dpd else False
    line_item['source'] = 'system'

    return line_item

def add_free_days_objects(query_result, response_object, request):
    free_days_types = ['detention', 'demurrage']

    if request['container_type'] == 'refer':
        free_days_types += ['plugin']

    for free_days_type in free_days_types:
        if query_result['data'].get(free_days_type):
            response_object[free_days_type] = (query_result['data'].get(free_days_type)) | ({'unit': 'per_container'})
        else:
            response_object[free_days_type] = {} | ({'unit': 'per_container'})

    if not response_object['detention'].get('free_limit'):
        response_object['detention']['free_limit'] = eval("DEFAULT_{}_DESTINATION_DETENTION".format(request['trade_type'].upper()))

    if not response_object['demurrage'].get('free_limit'):
        response_object['demurrage']['free_limit'] = eval("DEFAULT_{}_DESTINATION_DEMURRAGE".format(request['trade_type'].upper()))

    return True


def get_local_agent_ids(request):
    results = FclFreightRateLocalAgent.select(
        FclFreightRateLocalAgent.service_provider_id, FclFreightRateLocalAgent.location_type).where(
        FclFreightRateLocalAgent.location_id.in_([request['port_id'],request['country_id']]),
        FclFreightRateLocalAgent.trade_type == request['trade_type'],
        FclFreightRateLocalAgent.status == 'active'
    )

    result = [[str(model_to_dict(item)['service_provider_id']),model_to_dict(item)['location_type']] for item in results]
    if len(result) == 1:
        local_agent_ids = result[0][0]
    else:
        sorted_results = sorted([i for i in result if i[1] is not None], key = lambda x: LOCATION_HIERARCHY[x[1]])
        local_agent_ids = sorted_results[0][0] if sorted_results else None
    return local_agent_ids

def ignore_confirmed_inventory_rates(request, list):
    if request['include_confirmed_inventory_rates'] == True:
        return list

    rates = [rate for rate in list if rate['tags'] not in CONFIRMED_INVENTORY['tag']]
    return rates