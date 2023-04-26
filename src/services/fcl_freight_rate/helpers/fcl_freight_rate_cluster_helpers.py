from configs.fcl_freight_rate_constants import CONTAINER_CLUSTERS
from configs.definitions import FCL_FREIGHT_CHARGES
from services.fcl_freight_rate.models.fcl_freight_rate_extension_rule_set import FclFreightRateExtensionRuleSet
from peewee import *
from micro_services.client import maps
from playhouse.shortcuts import model_to_dict
from services.fcl_freight_rate.interaction.get_fcl_freight_commodity_cluster import get_fcl_freight_commodity_cluster
from fastapi import HTTPException

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
            raise HTTPException(status_code=400, detail= f"No cluster with {clusters['origin_location_cluster']['cluster_id']} found")


    if 'destination_location_cluster' in clusters and clusters['destination_location_cluster']:
        try:
            clusters['destination_location_cluster']['cluster_items'] = maps.get_location_cluster({'id': clusters['destination_location_cluster']['cluster_id']})['locations']
        except:
            raise HTTPException(status_code=400, detail= f"No cluster with {clusters['origin_location_cluster']['cluster_id']} found")

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
