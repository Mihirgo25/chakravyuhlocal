import json
from services.rail_rate.models.rail_rates_india import RailRatesIndia
from services.rail_rate.models.commodity_mapping import CommodityMapping

# Opening JSON file
f = open('/Users/cogoport/ocean-rms/res2.json')
commodity = open('/Users/cogoport/ocean-rms/commodity_mapping.json')
# returns JSON object as
# a dictionary
data = json.load(f)
commodity_data = json.load(commodity)
# Iterating through the json
# list
def insert():
    return
for i, data in data.items():
    print(i)
    print(data)
    for itr in data:
        try:
            RailRatesIndia.create(distance=float(i), load_type = itr['load'], class_type = itr['class'], base_rate = float(itr['price'], country_code = 'IN', currency = 'INR'))
        except:
            continue

# commodity mapping
for i, data in commodity_data.items():
    print(i)
    print(data)
    for itr in data:
        try:
            CommodityMapping.create(commodity_name=i, base_class = itr['load'], class_type = itr['class'], base_rate = float(itr['price']))
        except:
            continue


# Closing file
f.close()
