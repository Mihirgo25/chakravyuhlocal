from params import *
from peewee import *
from services.fcl_freight_rate.helpers.fcl_freight_rate_cluster_helpers import *
import copy
from micro_services.client import *
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.interaction.create_fcl_freight_rate import create_fcl_freight_rate_data
from configs.global_constants import MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT
from celery_worker import create_fcl_freight_rate_delay

def extend_create_fcl_freight_rate_data(request):
    if not isinstance(request, dict):
        request = request.dict(exclude_none=True)

    if request.get('extend_rates_for_lens'):
        request['mode']= 'cogo_lens'
        create_fcl_freight_rate_delay.apply_async(kwargs={'request':request},queue='fcl_freight_rate')
        return {"message":"Creating rates in delay"}

    if request.get('extend_rates'):
        rate_objects = get_fcl_freight_cluster_objects(request)
        if rate_objects:
            create_extended_rate_objects(rate_objects)
            return {"message":"Creating rates in delay"}


def create_extended_rate_objects(rate_objects):
    for rate_object in rate_objects:
        rate_object['mode']='rate_extension'
        create_fcl_freight_rate_delay.apply_async(kwargs={'request':rate_object},queue='fcl_freight_rate')

def get_fcl_freight_cluster_objects(request):
    fcl_freight_cluster_objects = []

    data = get_cluster_objects(request)

    if not data:
        return
    if request.get('rate_sheet_id'):
        cluster_objects = []
        for key, value in data.items():
            new_hash = value.copy()
            new_hash["cluster_type"] = str(key)
            cluster_objects.append(new_hash)
        required_mandatory_codes = get_required_mandatory_codes(cluster_objects)
        mandatory_codes = []
        for required_mandatory_code in required_mandatory_codes:
            for mandatory_code in required_mandatory_code['mandatory_codes']:
                mandatory_codes.append(mandatory_code)
        common_line_items = list(set([i['code'] for i in request['line_items'] if i is not None]).intersection(set(mandatory_codes)))
        if len(common_line_items) != len(set(mandatory_codes)):
            return

    try:
        origin_locations = [t['id'] for t in data['origin_location_cluster']['cluster_items']]
    except:
        origin_locations = [request['origin_port_id']]

    try:
        destination_locations = [t['id'] for t in data['destination_location_cluster']['cluster_items']]
    except:
        destination_locations = [request['destination_port_id']]

    if data.get('commodity_cluster'):
        commodities = data['commodity_cluster']['cluster_items']
        if commodities[request['container_type']]:
            commodities[request['container_type']] = commodities[request['container_type']]
        else:
            commodities[request['container_type']] = [request['commodity']]
    else:
        commodities = { request['container_type'] : [request['commodity']] }

    try:
        containers = data['container_cluster']['cluster_items']
    except:
        containers = [request['container_size']]

    icd_data = maps.list_locations({'filters':{ 'id': origin_locations + destination_locations , 'page_limit': MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT}})['list']

    new_data = {}
    for t in icd_data:
        new_data[t['id']]=t['is_icd']

    icd_data = new_data

    for origin_location in set(origin_locations):
        for destination_location in set(destination_locations):
            for container_type in commodities:
                for commodity in commodities[container_type]:
                    for container in containers:
                        param = copy.deepcopy(request)

                        if icd_data.get(origin_location) and not param.get('origin_main_port_id'):
                            param['origin_main_port_id'] = param['origin_port_id']
                        elif not icd_data.get(origin_location) and param.get('origin_main_port_id'):
                            param['origin_main_port_id'] = None
                        param['origin_port_id'] = origin_location

                        if icd_data.get(destination_location) and  not param.get('destination_main_port_id'):
                            param['destination_main_port_id'] = param['destination_port_id']
                        elif not icd_data.get(destination_location) and param.get('destination_main_port_id'):
                            param['destination_main_port_id'] = None

                        param['destination_port_id'] = destination_location

                        param['commodity'] = commodity
                        param['container_type'] = container_type
                        param['container_size'] = container

                        updated_param = add_mandatory_line_items(param,request)

                        for cluster in ['origin_location_cluster', 'destination_location_cluster', 'commodity_cluster', 'container_cluster']:
                            if data.get(cluster) and data[cluster]['line_item_charge_code'] and (data[cluster]['gri_rate'] or data[cluster]['gri_rate'] == 0) and data[cluster]['gri_currency']:
                                if (cluster == 'origin_location_cluster' and updated_param.get('origin_port_id') and updated_param['origin_location_port'] == request['origin_port_id']) or (cluster == 'destination_location_cluster' and updated_param.get('destination_port_id') and updated_param['destination_port_id'] == request['destination_port_id']) or  (cluster == 'commodity_cluster' and updated_param[commodity] == request[commodity]) or (cluster == 'container_cluster' and updated_param['container_size'] == request['container_size']) or (updated_param.get('origin_port_id') and updated_param.get('destination_port_id') and updated_param['origin_port_id'] == updated_param['destination_port_id']):
                                    continue
                                line_item = [t for t in updated_param['line_items'] if t['code'] == data[cluster]['line_item_charge_code']]

                                if not line_item:
                                    continue
                                line_item = line_item[0]
                                updated_param['line_items'].remove(line_item)
                                line_item['price'] = float(line_item['price']) + get_money_exchange(data[cluster]['gri_currency'], line_item['currency'], data[cluster]['gri_rate'])
                                updated_param['line_items'].append(line_item)

                        if request.get('extend_rates_for_existing_system_rates') or not check_rate_existence(updated_param):
                            if updated_param.get('origin_port_id') and updated_param.get('destination_port_id') and updated_param['origin_port_id'] != updated_param['destination_port_id']:
                                fcl_freight_cluster_objects.append(updated_param)
    for object in fcl_freight_cluster_objects:
        if (object['origin_port_id'] == request['origin_port_id'] and object['destination_port_id'] == request['destination_port_id'] and object['commodity'] == request['commodity'] and object['container_type'] == request['container_type'] and object['container_size'] == request['container_size']):
            fcl_freight_cluster_objects.remove(object)

    return fcl_freight_cluster_objects

def get_money_exchange(from_currency, to_currency, gri_rate):
    if not gri_rate:
        return 0
    result = common.get_money_exchange_for_fcl({'from_currency': from_currency, 'to_currency': to_currency, 'price': gri_rate})

    if result:
        return result['price']
    return 0

def add_mandatory_line_items(param,request):
    if not request.get('mandatory_charges'):
        return param
    commodity_mandatory_charges = [t for t in request['mandatory_charges']['required_mandatory_codes'] if t['cluster_type'] == param['commodity']]
    container_size_mandatory_charges = [t for t in request['mandatory_charges']['required_mandatory_codes'] if t['cluster_type'] == param['container_size']]
    commodity_type_mandatory_charges = [t for t in request['mandatory_charges']['required_mandatory_codes'] if t['cluster_type'] == param['container_type']]

    mandatory_charges = commodity_mandatory_charges + container_size_mandatory_charges + commodity_type_mandatory_charges

    existing_line_items = [t['code'] for t in param.get('line_items')]
    line_items = []

    if mandatory_charges:
        for t in mandatory_charges:
            line_items.extend(t['mandatory_codes'])
        missing_line_items = list(set(line_items).difference(set(existing_line_items)))
        if missing_line_items:
            for missing_line_item in missing_line_items:
                line_item = [t for t in request['mandatory_charges']['line_items'] if t['code'] == missing_line_item]
                if line_item:
                    param.get('line_items').append(line_item[0])
    return param


def check_rate_existence(updated_param):
    system_rate = FclFreightRate.select().where(FclFreightRate.origin_port_id == updated_param['origin_port_id'], FclFreightRate.destination_port_id == updated_param['destination_port_id'], FclFreightRate.container_size == updated_param['container_size'], FclFreightRate.commodity == updated_param['commodity'], FclFreightRate.container_type == updated_param['container_type'], FclFreightRate.service_provider_id == updated_param['service_provider_id'], FclFreightRate.shipping_line_id == updated_param['shipping_line_id'], FclFreightRate.last_rate_available_date > updated_param['validity_end']).execute()
    if system_rate:
        return True
    else:
        return False
