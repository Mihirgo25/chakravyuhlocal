from configs.fcl_freight_rate_constants import CONTAINER_CLUSTERS
from configs.definitions import FCL_FREIGHT_CHARGES
from services.fcl_freight_rate.models.fcl_freight_rate_extension_rule_set import FclFreightRateExtensionRuleSet
from peewee import *
from micro_services.client import maps
from playhouse.shortcuts import model_to_dict
from services.fcl_freight_rate.interaction.get_fcl_freight_commodity_cluster import get_fcl_freight_commodity_cluster
from fastapi import HTTPException
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
import copy
from micro_services.client import *
from rms_utils.get_in_batches import get_in_batches

def get_cluster_objects(rate_object):
    clusters = {}

    port_codes = maps.list_locations({'filters':{'id': [rate_object['origin_port_id'], rate_object['destination_port_id']]}})['list']

    param = {}
    for data in port_codes:
        param[data['id']] = data['port_code']

    port_codes = param

    cluster_data_q = FclFreightRateExtensionRuleSet.select().where(
        FclFreightRateExtensionRuleSet.cluster_reference_name << (
            port_codes.get(rate_object['origin_port_id']),
            port_codes.get(rate_object['destination_port_id']),
            rate_object['commodity'],
            rate_object['container_size']
        ) ,
        ((FclFreightRateExtensionRuleSet.service_provider_id == rate_object.get('service_provider_id')) | (FclFreightRateExtensionRuleSet.service_provider_id.is_null(True))),
        ((FclFreightRateExtensionRuleSet.shipping_line_id == rate_object.get('shipping_line_id'))  | (FclFreightRateExtensionRuleSet.shipping_line_id.is_null(True))),
        FclFreightRateExtensionRuleSet.status == 'active',
        (FclFreightRateExtensionRuleSet.trade_type <<  ('import', 'export') | FclFreightRateExtensionRuleSet.trade_type.is_null(True))
    ).execute()

    cluster_data = [model_to_dict(item) for item in cluster_data_q]

    for data in cluster_data:
        if data['cluster_reference_name'] == port_codes.get(rate_object['origin_port_id']) and (data['trade_type'] == 'export' or not data['trade_type']):
            if not 'origin_location_cluster' in clusters.keys():
                clusters['origin_location_cluster'] = data
        elif data['cluster_reference_name'] == port_codes.get(rate_object['destination_port_id']) and (data['trade_type'] == 'import' or not data['trade_type']):
            if not 'destination_location_cluster' in clusters.keys():
                clusters['destination_location_cluster'] = data
        elif data['cluster_reference_name'] == rate_object['commodity']:
            if not 'commodity_cluster' in clusters.keys():
                clusters['commodity_cluster'] = data
        elif data['cluster_reference_name'] == rate_object['container_size']:
            if not 'container_cluster' in clusters.keys():
                clusters['container_cluster'] = data


    if 'origin_location_cluster' in clusters and clusters['origin_location_cluster']:
        try:
            clusters['origin_location_cluster']['cluster_items'] = maps.get_location_cluster({'id': clusters['origin_location_cluster']['cluster_id']})['locations']
        except:
            raise HTTPException(status_code=499, detail= f"No cluster with {clusters['origin_location_cluster']['cluster_id']} found")


    if 'destination_location_cluster' in clusters and clusters['destination_location_cluster']:
        try:
            clusters['destination_location_cluster']['cluster_items'] = maps.get_location_cluster({'id': clusters['destination_location_cluster']['cluster_id']})['locations']
        except:
            raise HTTPException(status_code=499, detail= f"No cluster with {clusters['origin_location_cluster']['cluster_id']} found")

    if 'commodity_cluster' in clusters and clusters['commodity_cluster']:
        clusters['commodity_cluster']['cluster_items'] = get_fcl_freight_commodity_cluster(clusters['commodity_cluster']['cluster_id'])['commodities']

    if 'container_cluster' in clusters and clusters['container_cluster']:
        clusters['container_cluster']['cluster_items'] = CONTAINER_CLUSTERS[clusters['container_cluster']['cluster_id']]

    return clusters

def get_required_mandatory_codes(cluster_objects):
    required_mandatory_codes = []
    commodity_cluster_items = []
    container_size_cluster_items = []
    cluster_container_type = []
    commodity_cluster_object = [i for i in cluster_objects if i['cluster_type']== 'commodity_cluster']
    if commodity_cluster_object:
        commodity_cluster_items = list(commodity_cluster_object[0]['cluster_items'].values())
        cluster_container_type = list(commodity_cluster_object[0]['cluster_items'].keys())
    commodity_cluster_items = [item for cluster in commodity_cluster_items for item in cluster]

    container_cluster_object = [i for i in cluster_objects if i['cluster_type']== 'container_cluster']

    if container_cluster_object:
        container_size_cluster_items = container_cluster_object[0]['cluster_items']

    all_cluster_items = commodity_cluster_items + container_size_cluster_items + cluster_container_type

    for cluster_item in all_cluster_items:
        if cluster_item in commodity_cluster_items:
            commodity = cluster_item
        if cluster_item in container_size_cluster_items:
            container_size = cluster_item
        if cluster_item in cluster_container_type:
            container_type = cluster_item
        mandatory_codes = []
        fcl_freight_charges_dict = FCL_FREIGHT_CHARGES

        for code, config in fcl_freight_charges_dict.items():
            condition_value = True
            condition = str(config['condition'])
            try:
                if condition != 'True':
                    condition_value = eval(condition)
            except:
                continue

            if not condition_value:
                continue
            if 'mandatory' in config['tags']:
                    mandatory_codes.append(code)


        if mandatory_codes:
            mandatory_code = { 'cluster_type': cluster_item, 'mandatory_codes': mandatory_codes }

        if mandatory_code:
            required_mandatory_codes.append(mandatory_code)
    return required_mandatory_codes

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
    
def get_money_exchange(from_currency, to_currency, gri_rate):
    if not gri_rate:
        return 0
    result = common.get_money_exchange_for_fcl({'from_currency': from_currency, 'to_currency': to_currency, 'price': gri_rate})

    if result:
        return result['price']
    return 0

def get_locations(location_ids: list = [], BATCH_SIZE = 500):
    locations = maps.list_locations({'filters':{ 'id': location_ids , 'page_limit': BATCH_SIZE }})['list']
    return locations or []

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
        mandatory_codes = list(set(mandatory_codes))
        # if len(common_line_items) != len(set(mandatory_codes)):
        #     return

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
    
    location_ids = origin_locations + destination_locations
    icd_data = get_in_batches(method=get_locations, to_batch_params=location_ids, BATCH_SIZE=500)

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