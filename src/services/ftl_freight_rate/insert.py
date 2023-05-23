import os, json
from services.ftl_freight_rate.models.ftl_freight_rate_rule_set import (
    FtlFreightRateRuleSet,
)

path_to_json = "/Users/mithilanchan/CogoBack/chakravyuh/.data"
json_files = [
    pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith(".json")
]


def insert():
    for index, js in enumerate(json_files):
        with open(os.path.join(path_to_json, js)) as json_file:
            json_text = json.load(json_file)
            i = 0
            for data in json_text:
                
                row_data = {
                'location_id': '541d1232-58ce-4d64-83d6-556a42209eb7',
                'location_type': 'country',
                'truck_type': data['truck_type'],
                'process_type': data['process_type'],
                'process_unit': data['process_unit'],
                'process_value':data['process_value'],
                'process_currency': 'INR',
                'status': 'active',
                }
                
                FtlFreightRateRuleSet.create(**row_data)
                i = i + 1
                print(i)
                print(row_data)
