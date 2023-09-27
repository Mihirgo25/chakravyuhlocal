from libs.get_applicable_filters import is_valid_uuid
from micro_services.client import *
from database.rails_db import get_operators

def process_conditions(condition_value, condition_key):
    if condition_key in ["origin_country_id", "destination_country_id", "origin_port_id", "destination_port_id", "terminal_id"]:
        locations_data = maps.list_locations({"filters": {"id": condition_value}})["list"]
        locations_data = [location["name"] for location in locations_data]
        return locations_data
    elif condition_key == "shipping_line_id":
        shipping_line_data = get_operators(id=condition_value)
        shipping_line_data = [shipping_line["short_name"] for shipping_line in shipping_line_data]
        return shipping_line_data


def get_parsed_conditions_data(line_items):
    parsed_line_items = []
    for item in line_items:
        if item.get('conditions'):
            values = item["conditions"]["values"]
            for conditions in values:
                condition_value = conditions["condition_value"]
                if isinstance(condition_value, str) and  is_valid_uuid(condition_value):
                    new_condition_value = process_conditions([condition_value], conditions["condition_key"])
                    conditions['condition_value'] = new_condition_value
                elif isinstance(condition_value, list):
                    new_condition_value = process_conditions(condition_value, conditions["condition_key"])
                    conditions['condition_value'] = new_condition_value

            parsed_line_items.append(item)
        else:
            parsed_line_items.append(item)

    return parsed_line_items
