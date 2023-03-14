from params import LineItem,FreeDay
from rails_client import client
import yaml
from configs.defintions import FCL_FREIGHT_LOCAL_CHARGES
from pydantic import BaseModel
from configs.fcl_freight_rate_constants import HAZ_CLASSES

class FclFreightRateLocalData(BaseModel):
    line_items: list[LineItem] = []
    detention: FreeDay = None
    demurrage: FreeDay = None
    plugin: FreeDay = None
    def __init__(self,data):
        if data:
            super().__init__(line_items = data.get('line_items'),detention =data.get('detention'),demurrage = data.get('demurrage'),plugin = data.get("plugin") )
        else:
            super().__init__()

    def validate_duplicate_charge_codes(self):
        if len(set([(t.code, t.location_id) for t in self.line_items])) == len(self.line_items):
            return True
        # raise HTTPException(status_code=499, detail="line item contains duplicate")
        return False
    def validate_invalid_charge_codes(self, possible_charge_codes):
        invalid_line_items = [str(t.code) for t in self.line_items if str(t.code) not in possible_charge_codes]
        print(invalid_line_items)
        if invalid_line_items:
            return False
        return True
            # self.parent.errors.add('line_items', f"{', '.join(invalid_line_items)} are invalid")

    def get_line_item_messages(self, port, main_port, shipping_line, container_size, container_type, commodity, trade_type, possible_charge_codes):
        with open(FCL_FREIGHT_LOCAL_CHARGES, 'r') as file:
            fcl_freight_local_charges_dict = yaml.safe_load(file)

        location_ids = list(set([item.location_id for item in self.line_items if item.location_id is not None]))
        locations = {}

        if location_ids:
            locations = client.ruby.get_multiple_service_objects_data_for_fcl({'objects': [{'name': 'location','filters': { 'id': location_ids },'fields': ['id', 'type', 'country_code']}]})['list']['location'] #check this

        line_items_error_messages = {}
        line_items_info_messages = {}
        is_line_items_error_messages_present = False
        is_line_items_info_messages_present = False

        grouped_charge_codes = {}
        for line_item in self.line_items:
            grouped_charge_codes[line_item.code] = line_item.__dict__

        for code, line_items in grouped_charge_codes.items():
            code_config = fcl_freight_local_charges_dict[code]

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

            # if any(unit not in code_config.get('units', []) for unit in [li.unit for li in line_items]):
            #     line_items_error_messages[code] = [f"can only be having units {', '.join(code_config.get('units', []))}"]
            #     is_line_items_error_messages_present = True
            #     continue

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

            if len(code_config.get('locations', [])) > 0 and ((locations['location_id']['type'] != 'country') or (locations['location_id']['country_code'].upper() == code_config.get('locations', []))):
                line_items_error_messages[code] = [f"can only contain locations {', '.join(code_config['locations'])}"]
                is_line_items_error_messages_present = True
                continue

        for code, config in possible_charge_codes.items():
            if 'mandatory' in config.get('tags', []) and not config.get('locations'):
                # code = str(code)
                if code not in grouped_charge_codes:
                    line_items_error_messages[code] = ['is not present']
                    is_line_items_error_messages_present = True

        # for code, config in possible_charge_codes.items():
        #     if config.get('locations'):
        #         location_codes = config['locations'] or []
        #         required_code_specific_locations = client.ruby.get_multiple_service_objects_data_for_fcl(
        #             objects=[{
        #                 'name': 'location',
        #                 'filters': {'type': 'country', 'country_code': location_codes},
        #                 'fields': ['name']
        #             }]
        #         )['list']
        # # try:
        #     for code, config in filter(lambda x: x[1]['locations'], possible_charge_codes.items()):
        #         # code = str(code)
        #         location_codes = config['locations'] or []
        #         required_code_specific_locations = client.ruby.get_multiple_service_objects_data_for_fcl(
        #             objects=[{
        #                 'name': 'location',
        #                 'filters': {'type': 'country', 'country_code': location_codes},
        #                 'fields': ['name']
        #             }]
        #         )['list'][0]['location']

        #         location_names = [data['name'] for _, data in required_code_specific_locations.items()]
        #         if not location_names:
        #             continue

        #         if not grouped_charge_codes[code]:
        #             line_items_info_messages[code] = ["is required for serving in " + ', '.join(location_names)]
        #             is_line_items_info_messages_present = True
        #         else:
        #             given_code_specific_location_ids = set(line_item.location_id for line_item in grouped_charge_codes[code])
        #             remaining_code_specific_location_ids = set(required_code_specific_locations.keys()) - given_code_specific_location_ids
        #             if not remaining_code_specific_location_ids:
        #                 continue

        #             line_items_info_messages[code] = ["is required for serving in " + ', '.join(
        #                 required_code_specific_locations[id]['name'] for id in remaining_code_specific_location_ids)]
        #             is_line_items_info_messages_present = True
        # except Exception as e:
        #     print(e)
        # print('ok')
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
