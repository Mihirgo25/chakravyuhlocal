from params import *
from peewee import * 
from services.fcl_freight_rate.helpers.fcl_freight_rate_cluster_helpers import *
import copy
from rails_client import client
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.interaction.create_fcl_freight_rate import create_fcl_freight_rate_data
from configs.global_constants import MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT

def extend_create_fcl_freight_rate_data(request):
    
    if request.extend_rates_for_lens:
        temp = create_fcl_freight_rate_data(request.dict(exclude_none=True))
        return temp

    if request.extend_rates:
        rate_objects = get_fcl_freight_cluster_objects(request.dict(exclude_none=True),request)
        if rate_objects:
            temp1 = create_extended_rate_objects(rate_objects)
            return temp1

def create_extended_rate_objects(rate_objects):
    for rate_object in rate_objects:
        temp = create_fcl_freight_rate_data(rate_object)
    return temp

def get_fcl_freight_cluster_objects(rate_object,request):
    fcl_freight_cluster_objects = []

    data = get_cluster_objects(rate_object)

    if not data:
        return
    if request.rate_sheet_id:
        cluster_objects = []
        for key, value in data.items():
            new_hash = value.copy()
            new_hash["cluster_type"] = str(key)
            cluster_objects.append(new_hash)
        required_mandatory_codes = get_required_mandatory_codes(cluster_objects)
        common_line_items = set([i for i in rate_object['line_items']['code'] if i is not None]) and set([i for i in required_mandatory_codes['mandatory_codes'] if i is not None])
        if common_line_items.__len__ != set([i for i in required_mandatory_codes['mandatory_codes'] if i is not None]).__len__:
            return

    try:
        origin_locations = [t['id'] for t in data['origin_location_cluster']['cluster_items']]
    except:
        origin_locations = [rate_object['origin_port_id']]

    try:
        destination_locations = [t['id'] for t in data['destination_location_cluster']['cluster_items']]
    except:
        destination_locations = [rate_object['destination_port_id']]

    if data.get('commodity_cluster'):
        commodities = data['commodity_cluster']['cluster_items']
        if commodities[rate_object['container_type']]:
            commodities[rate_object['container_type']] = commodities[rate_object['container_type']] or [rate_object['commodity']]
        else:
            commodities[rate_object['container_type']] = [rate_object['commodity']]
    else:
        commodities = { rate_object['container_type'] : [rate_object['commodity']] }

    try:    
        containers = [rate_object['container_size']] or data['container_cluster']['cluster_items'] 
    except:
        containers = [rate_object['container_size']]

    icd_data = client.ruby.list_locations({'filters': { 'id': origin_locations + destination_locations }, 'page_limit': MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT})['list']

    new_data = {}
    for t in icd_data:
        new_data[t['id']]=t['is_icd']
    
    icd_data = new_data

    for origin_location in set(origin_locations):
        for destination_location in set(destination_locations):
            for container_type in commodities:
                for commodity in commodities[container_type]:
                    for container in containers:
                        param = copy.deepcopy(rate_object)

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
                            if data.get(cluster) and data[cluster]['line_item_charge_code'] and data[cluster]['gri_rate'] and data[cluster]['gri_currency']:
                                if (cluster == 'origin_location_cluster' and updated_param['origin_port_id'] and updated_param['origin_location_port'] == rate_object['origin_port_id']) or (cluster == 'destination_location_cluster' and updated_param['destination_port_id'] and updated_param['destination_port_id'] == rate_object['destination_port_id']) or  (cluster == 'commodity_cluster' and updated_param[commodity] == rate_object[commodity]) or (cluster == 'container_cluster' and updated_param['container_size'] == rate_object['container_size']) or (updated_param['origin_port_id'] and updated_param['destination_port_id'] and updated_param['origin_port_id'] == updated_param['destination_port_id']):
                                    continue
                                line_item = [t for t in updated_param['line_items'] if t['code'] == data[cluster]['line_item_charge_code']][0]

                                if not line_item:
                                    continue
                                updated_param['line_items'].remove(line_item)
                                line_item['price'] = float(line_item['price']) + client.ruby.get_money_exchange_for_fcl(data[cluster]['gri_currency'], line_item['currency'], data[cluster]['gri_rate'])
                                updated_param['line_items'].append(line_item)

                        if request.extend_rates_for_existing_system_rates or not check_rate_existence(updated_param):
                            if updated_param.get('origin_port_id') and updated_param.get('destination_port_id') and updated_param['origin_port_id'] != updated_param['destination_port_id']:
                                fcl_freight_cluster_objects.append(updated_param)
    for i in fcl_freight_cluster_objects:
        if (i['origin_port_id'] == rate_object['origin_port_id'] and i['destination_port_id'] == rate_object['destination_port_id'] and i['commodity'] == rate_object['commodity'] and i['container_type'] == rate_object['container_type'] and i['container_size'] == rate_object['container_size']):
            fcl_freight_cluster_objects.remove(i)
    return fcl_freight_cluster_objects

def add_mandatory_line_items(param,request):
    if not request.mandatory_charges:
        return param

    commodity_mandatory_charges = [t for t in request.mandatory_charges.required_mandatory_codes if t['cluster_type'] == param['commodity']]
    container_size_mandatory_charges = [t for t in request.mandatory_charges.required_mandatory_codes if t['cluster_type'] == param['container_size']]
    commodity_type_mandatory_charges = [t for t in request.mandatory_charges.required_mandatory_codes if t['cluster_type'] == param['container_type']]

    mandatory_charges = commodity_mandatory_charges + container_size_mandatory_charges + commodity_type_mandatory_charges
    existing_line_items = [t['code'] for t in param.get('line_items')]
    missing_line_items = []
    if mandatory_charges:
        missing_line_items = mandatory_charges['mandatory_codes'].flatten() - existing_line_items
    
    if missing_line_items:
        for missing_line_item in missing_line_items:
            param.get('line_items').append([t for t in request.mandatory_charges.line_items if t['code'] == missing_line_item][0])

    return param


def check_rate_existence(updated_param):
    system_rate = FclFreightRate.select().where(FclFreightRate.origin_port_id == updated_param['origin_port_id'] and FclFreightRate.destination_port_id == updated_param['destination_port_id'] and FclFreightRate.container_size == updated_param['container_size'] and FclFreightRate.commodity == updated_param['commodity'] and FclFreightRate.container_type == updated_param['container_type'] and FclFreightRate.service_provider_id == updated_param['service_provider_id'] and FclFreightRate.shipping_line_id == updated_param['shipping_line_id'] and FclFreightRate.last_rate_available_date > updated_param['validity_end']).execute()
    if system_rate:
        return True
    else:
        return False