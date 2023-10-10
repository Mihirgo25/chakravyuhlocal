from libs.get_applicable_filters import is_valid_uuid
from micro_services.client import *
from database.rails_db import get_operators

LOCATION_IDS = ["origin_country_id", "destination_country_id", "origin_port_id", "destination_port_id", "terminal_id"]

def get_location_and_shipping_line_mappings(all_location_ids, all_shipping_line_ids):
    location_mappings = {}
    shipping_line_mappings = {}
    if all_location_ids:
        locations_data  = maps.list_locations({ 'filters': { 'id': all_location_ids }, 'includes': {'id': True, 'name': True}, 'page_limit': 1000, 'page': 1})['list']
        location_mappings = {location['id']: location['name'] for location in locations_data}
    if all_shipping_line_ids:
        shipping_lines_data = get_operators(id = all_shipping_line_ids,operator_type = 'shipping_line')
        shipping_line_mappings = {shipping_line['id']: shipping_line['short_name'] for shipping_line in shipping_lines_data}
    return location_mappings, shipping_line_mappings

def get_location_and_shipping_line_ids(line_items):
    all_location_ids = []
    all_shipping_line_ids = []
    for item in line_items:
        if item.get('conditions'):
            values = item["conditions"]["values"]
            for conditions in values:
                condition_value = conditions["condition_value"]
                condition_key = conditions['condition_key']
                if condition_key == 'shipping_line_id':
                    if isinstance(condition_value, str) and is_valid_uuid(condition_value):
                        all_shipping_line_ids.append(condition_value)
                    elif isinstance(condition_value, list):
                        all_shipping_line_ids.extend(condition_value)
                elif condition_key in LOCATION_IDS:
                    if isinstance(condition_value, str) and is_valid_uuid(condition_value):
                        all_location_ids.append(condition_value)
                    elif isinstance(condition_value, list):
                        all_location_ids.extend(condition_value)
    return all_location_ids, all_shipping_line_ids

def map_ids_to_names(ids, mappings):
    if not mappings:
        return [] 
    if isinstance(ids, str):
        return [mappings[ids]]
    elif isinstance(ids, list):
        return [mappings[id] for id in ids]

def get_parsed_conditions_data(line_items):
    parsed_line_items = []
    location_ids, shipping_line_ids = get_location_and_shipping_line_ids(line_items)
    location_mappings, shipping_line_mappings = get_location_and_shipping_line_mappings(location_ids, shipping_line_ids)
    
    for item in line_items:
        if item.get('conditions'):
            values = item["conditions"]["values"]
            for conditions in values:
                condition_value = conditions["condition_value"]
                condition_key = conditions["condition_key"]
                if condition_key == 'shipping_line_id':
                    conditions['parsed_value'] = map_ids_to_names(condition_value, shipping_line_mappings)               
                elif condition_key in LOCATION_IDS:
                    conditions['parsed_value'] = map_ids_to_names(condition_value, location_mappings)
                else:
                    conditions['parsed_value'] = conditions['condition_value']
            parsed_line_items.append(item)
        else:
            parsed_line_items.append(item)

    return parsed_line_items
