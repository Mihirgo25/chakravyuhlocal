from libs.get_applicable_filters import is_valid_uuid
from micro_services.client import *
from database.rails_db import get_operators

LOCATION_IDS = ["origin_country_id", "destination_country_id", "origin_port_id", "destination_port_id", "terminal_id"]

def ids_mappings(all_location_ids, all_shipping_line_ids):
    locations_data  = maps.list_locations({ 'filters': { 'id': all_location_ids }})['list']
    shipping_lines_data = get_operators(id = all_shipping_line_ids,operator_type = 'shipping_line')
    location_mappings = {location['id']: location['name'] for location in locations_data}
    shipping_line_mappings = {shipping_line['id']: shipping_line['short_name'] for shipping_line in shipping_lines_data}
    return location_mappings, shipping_line_mappings

def extract_ids(line_items):
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

def parse_ids(ids, mappings):
    if isinstance(ids, str):
        return [mappings[ids]]
    elif isinstance(ids, list):
        return [mappings[value] for value in ids]

def get_parsed_conditions_data(line_items):
    parsed_line_items = []
    location_ids, shipping_line_ids = extract_ids(line_items)
    location_mappings, shipping_line_mappings = ids_mappings(location_ids, shipping_line_ids)
    
    for item in line_items:
        if item.get('conditions'):
            values = item["conditions"]["values"]
            for conditions in values:
                condition_value = conditions["condition_value"]
                condition_key = conditions["condition_key"]
                if condition_key == 'shipping_line_id':
                    conditions['condition_value'] = parse_ids(condition_value, shipping_line_mappings)               
                elif condition_key in LOCATION_IDS:
                    conditions['condition_value'] = parse_ids(condition_value, location_mappings)
            parsed_line_items.append(item)
        else:
            parsed_line_items.append(item)

    return parsed_line_items
