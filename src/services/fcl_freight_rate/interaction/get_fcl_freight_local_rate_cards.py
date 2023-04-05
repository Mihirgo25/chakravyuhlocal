from services.fcl_freight_rate.models.fcl_freight_rate_local import FclFreightRateLocal
from services.fcl_freight_rate.models.fcl_freight_rate_local_agent import FclFreightRateLocalAgent
from configs.global_constants import HAZ_CLASSES,CONFIRMED_INVENTORY, PREDICTED_RATES_SERVICE_PROVIDER_IDS
from configs.fcl_freight_rate_constants import LOCATION_HIERARCHY, DEFAULT_EXPORT_DESTINATION_DETENTION, DEFAULT_IMPORT_DESTINATION_DETENTION, DEFAULT_EXPORT_DESTINATION_DEMURRAGE, DEFAULT_IMPORT_DESTINATION_DEMURRAGE, DEFAULT_LOCAL_AGENT_IDS
from configs.definitions import FCL_FREIGHT_LOCAL_CHARGES
from fastapi.encoders import jsonable_encoder

def get_fcl_freight_local_rate_cards(request): 
    try: 
        if 'rates' in request and request['rates']:
            rate_list = build_response_list(request['rates'], request)

            return {'list': rate_list }

        local_query = initialize_local_query(request)

        local_query_results = jsonable_encoder(list(local_query.dicts()))

        rate_list = build_response_list(local_query_results, request)

        return {'list' : rate_list }
    except Exception as e:
        print(e)
        return { "list": [] }


def initialize_local_query(request):
    country_id = request["country_id"]
    default_lsp = DEFAULT_LOCAL_AGENT_IDS["default"]["value"]
    if country_id in DEFAULT_LOCAL_AGENT_IDS:
        default_lsp = DEFAULT_LOCAL_AGENT_IDS[country_id]["value"]
    
    service_provider_ids = [default_lsp]
    local_agents = get_local_agent_ids(request)
    if local_agents:
        service_provider_ids.append(get_local_agent_ids(request))
    if request['service_provider_id']:
        service_provider_ids.append(request['service_provider_id'])

    query = FclFreightRateLocal.select(
        FclFreightRateLocal.service_provider_id,
        FclFreightRateLocal.main_port_id,
        FclFreightRateLocal.shipping_line_id,
        FclFreightRateLocal.data
        ).where(
        FclFreightRateLocal.port_id == request['port_id'], 
        FclFreightRateLocal.container_size == request['container_size'], 
        FclFreightRateLocal.container_type == request['container_type'], 
        FclFreightRateLocal.trade_type == request['trade_type'],
        ~ FclFreightRateLocal.is_line_items_error_messages_present,
        FclFreightRateLocal.service_provider_id.in_(service_provider_ids))

    if request['commodity'] in HAZ_CLASSES:
        query = query.where(FclFreightRateLocal.commodity == request['commodity'])
    else:
        query = query.where(FclFreightRateLocal.commodity == None)
    
    if request['shipping_line_id']:
        query = query.where(FclFreightRateLocal.shipping_line_id == request['shipping_line_id'])

    return query


def build_response_list(query_results, request):
    response_list = []
    for result in query_results:
        response_object = build_response_object(result, request)
        if not response_object:
            continue

        response_list.append(response_object)
    return response_list

def build_response_object(result, request):
    response_object = {
      'service_provider_id': result['service_provider_id'],
      'main_port_id': result['main_port_id'],
      'shipping_line_id': result['shipping_line_id'],
      'source': 'predicted' if result['service_provider_id'] in PREDICTED_RATES_SERVICE_PROVIDER_IDS else 'spot_rates',
      'tags': []
    }

    if response_object['service_provider_id'] in CONFIRMED_INVENTORY['service_provider_ids']:
        response_object['tags'].append(CONFIRMED_INVENTORY['tag'])

    build_local_line_items(result, response_object, request)

    add_free_days_objects(result, response_object, request)

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
    
    # commented by @ssngurjar ask before removing

    # if (len(list(set(request['additional_services']).difference([item['code'] for item in response_object['line_items']])))) > 0:
    #     return False

    # if response_object['line_items']:
    #     return True   

def build_local_line_item_object(line_item, request):
    fcl_freight_local_charges = FCL_FREIGHT_LOCAL_CHARGES

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
        slab = [t for t in line_item['slabs'] if (t['lower_limit'] <= slab_value) and (t['upper_limit'] >= slab_value)]
        if slab:
            slab = slab[0]
            line_item['price'] = slab['price']
            line_item['currency'] = slab['currency']
    line_item = {
        "code": line_item["code"],
        "unit": line_item["unit"],
        "price": line_item["price"],
        "currency": line_item["currency"],
        "remarks": line_item["remarks"] if 'remarks' in line_item else []
    }
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
            if (query_result['data'].get(free_days_type)):
                response_object[free_days_type] = (query_result['data'].get(free_days_type)) | ({'unit': 'per_container'})
        else:
            response_object[free_days_type] = {'unit': 'per_container'} 

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
    results = jsonable_encoder(list(results.dicts()))

    new_results = []
    for item in results:
        new_results.append([item['service_provider_id'],item['location_type']])

    if len(new_results) == 1:
        local_agent_ids = new_results[0][0]
    else:
        sorted_results = sorted([i for i in new_results if i[1] is not None], key = lambda x: LOCATION_HIERARCHY[x[1]])
        local_agent_ids = sorted_results[0][0] if sorted_results else None
    return local_agent_ids

def ignore_confirmed_inventory_rates(request, list):
    if request['include_confirmed_inventory_rates'] == True:
        return list

    rates = [rate for rate in list if rate['tags'] not in CONFIRMED_INVENTORY['tag']]
    return rates