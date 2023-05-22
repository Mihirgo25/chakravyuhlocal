import json
from services.haulage_freight_rate.models.haulage_freight_rate_rule_sets import HaulageFreightRateRuleSet


def insert():
    # Opening JSON file
    f = open('/Users/cogoport/chakravyuh/.data/NEW.json')
    # returns JSON object as
    # a dictionary
    data = json.load(f)
    # Iterating through the json
    # list
    for i, data in data.items():
        print(i)
        print(data)
        for itr in data:
            # try:
            HaulageFreightRateRuleSet.create(distance=float(i), train_load_type = itr['load'], commodity_class_type = itr['class'], base_price = float(itr['price']), country_code = 'IN', currency = 'INR')
            # except:
            #     continue
    f.close()
    return

def insert_china():
    # Opening JSON file
    f = open('/Users/cogoport/chakravyuh/.data/china_data.json')
    # returns JSON object as
    # a dictionary
    data = json.load(f)
    # Iterating through the json
    # list
    j = 1
    for i, data in data.items():
        # try:
        print(j)
        HaulageFreightRateRuleSet.create(distance=1, train_load_type = 'Wagon Load', commodity_class_type = 'default', base_price = float(data['base_price']), country_code = 'CN', currency = 'CNY', base_price_unit = data['base_price_unit'], running_base_price = float(data['running_base_price']), running_base_price_unit = data['running_base_price_unit'], container_type = i)
        # except:
        #     continue'
        j+=1
    f.close()
    return



