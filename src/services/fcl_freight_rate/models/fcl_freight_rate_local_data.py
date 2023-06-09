from params import LineItem,FreeDay
from configs.definitions import FCL_FREIGHT_LOCAL_CHARGES
from pydantic import BaseModel
from configs.fcl_freight_rate_constants import HAZ_CLASSES
from micro_services.client import common, maps

class FclFreightRateLocalData(BaseModel):
    line_items: list[LineItem] = []
    detention: FreeDay = None
    demurrage: FreeDay = None
    plugin: FreeDay = None
    def __init__(self,data):
        if data:
            new_data = {}
            for key in data.keys():
                if data[key]:
                    new_data[key] = data[key]
                    if isinstance(data[key], list) and key == 'line_items':
                        for item in new_data[key]:
                            if 'remarks' in item and item.get('remarks'):
                                item['remarks'] = list(filter(None, item['remarks']))

            super().__init__(**new_data)
        else:
            super().__init__()

    def validate_duplicate_charge_codes(self):
        if len(set([(t.code, t.location_id) for t in self.line_items])) == len(self.line_items):
            return True
        return False

    def validate_invalid_charge_codes(self, possible_charge_codes):
        invalid_line_items = [str(t.code) for t in self.line_items if str(t.code) not in possible_charge_codes]
        return invalid_line_items


    def get_line_item_messages(self, port, main_port, shipping_line_id, container_size, container_type, commodity, trade_type, possible_charge_codes):
        fcl_freight_local_charges_dict = FCL_FREIGHT_LOCAL_CHARGES

        location_ids = list(set([item.location_id for item in self.line_items if item.location_id is not None]))
        locations = []

        if location_ids:
            locations = maps.list_locations({'filters': { 'id': location_ids }})['list']

        line_items_error_messages = {}
        line_items_info_messages = {}
        is_line_items_error_messages_present = False
        is_line_items_info_messages_present = False

        grouped_charge_codes = {}
        for line_item in self.line_items:
            grouped_charge_codes[line_item.code] = line_item.__dict__


        for code, line_items in grouped_charge_codes.items():
            code_config = fcl_freight_local_charges_dict.get(code)

            if not code_config:
                line_items_error_messages[code] = ['is invalid']
                is_line_items_error_messages_present = True
                continue

            if trade_type not in code_config['trade_types']:
                line_items_error_messages[code] = [f"can only be added for {', '.join(code_config['trade_types'])}"]
                is_line_items_error_messages_present = True
                continue

            if line_items['unit'] not in code_config['units']:
                line_items_error_messages[code] = [f"can only be having units {', '.join(code_config['units'])}"]
                is_line_items_error_messages_present = True
                continue

            if not eval(str(code_config['condition'])):
                line_items_error_messages[code] = ['is invalid']
                is_line_items_error_messages_present = True
                continue

            if ('slab_cargo_weight_per_container' in code_config['tags'] or 'slab_containers_count' in code_config['tags']) and len(line_items['slabs']) ==  0:
                line_items_info_messages[code] = ['can contain slab basis rates for higher conversion']
                is_line_items_info_messages_present = True
                continue

            if len(code_config.get('locations', [])) == 0 and line_items.get('location_id') and len(line_items.get('location_id',[])) > 0:
                line_items_error_messages[code] = ['can not be added with location']
                is_line_items_error_messages_present = True
                continue

            if len(code_config.get('locations', [])) > 0 and line_items.get('location_id') and len(line_items.get('location_id',[])) == 0:
                line_items_error_messages[code] = ['can only be added with location']
                is_line_items_error_messages_present = True
                continue

            if len(code_config.get('locations', [])) > 0:
                if any(location['type']!='country' or location['country_code'].upper() not in code_config.get('locations',[]) for location in locations):
                    line_items_error_messages[code] = [f"can only contain locations {', '.join(code_config['locations'])}"]
                    is_line_items_error_messages_present = True
                    continue

        for code, config in possible_charge_codes.items():
            if 'mandatory' in config.get('tags', []) and not config.get('locations'):
                if code not in grouped_charge_codes:
                    line_items_error_messages[code] = ['is not present']
                    is_line_items_error_messages_present = True

        for code, config in possible_charge_codes.items():
            if 'carrier_haulage' in config.get('tags', []):
                if grouped_charge_codes.get(code) is None and not line_items_error_messages.get(code):
                    line_items_info_messages[code] = ['can be added as carrier haulage for more conversion']
                    is_line_items_info_messages_present = True

        for code, config in possible_charge_codes.items():
            if 'dpd' in config.get('tags', []):
                if grouped_charge_codes.get(code) is None and not line_items_error_messages.get(code):
                    line_items_info_messages[code] = ['can be added as dpd for more conversion']
                    is_line_items_info_messages_present = True

        for code, config in possible_charge_codes.items():
            if 'additional_service' in config.get('tags', []):
                if grouped_charge_codes.get(code) is None and not line_items_error_messages.get(code):
                    line_items_info_messages[code] = ['can be added for more conversion']
                    is_line_items_info_messages_present = True

        return {
        'line_items_error_messages': line_items_error_messages,
        'is_line_items_error_messages_present': is_line_items_error_messages_present,
        'line_items_info_messages': line_items_info_messages,
        'is_line_items_info_messages_present': is_line_items_info_messages_present
        }
