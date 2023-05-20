import os, json
from services.trailer_freight_rates.models.trailer_freight_rate_constant import TrailerFreightRateCharges

path_to_json = "/Users/cogoport/Desktop/cogoport/chakravyuh/.data"

json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]

def insert():
    for index, js in enumerate(json_files):
        with open(os.path.join(path_to_json, js)) as json_file:
            json_text = json.load(json_file)
            i = 0 
            for data in json_text:
                row = {
                    'country_code' : data['country_code'],
                    'currency_code' : data['currency_code'],
                    'status' : data['status'],
                    'nh_toll' : data['nh_toll'],
                    'tyre' : data['tyre'],
                    'driver' : data['driver'],
                    'document' : data['document'],
                    'handling' : data['handling'],
                    'maintanance' : data['maintanance'],
                    'misc' : data['misc']
                }
                TrailerFreightRateCharges.create(**row)
                i = i + 1
                print(i)
                print(row)
