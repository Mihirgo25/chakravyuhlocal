data = {
    "1 ton box": {
        "base_price": "0.021",
        "base_price_unit": "USD/box",
        "running_base_price": "0.000089",
        "running_base_price_unit": "USD/carton kilometer"
    },
    "10 ton box": {
        "base_price": "12.10",
        "base_price_unit": "USD/box",
        "running_base_price": "0.054",
        "running_base_price_unit": "USD/carton kilometer"
    },
    "20": {
        "base_price": "22.59",
        "base_price_unit": "USD/box",
        "running_base_price": "0.10",
        "running_base_price_unit": "USD/carton kilometer"
    },
    "40": {
        "base_price": "44.16",
        "base_price_unit": "USD/box",
        "running_base_price": "0.20",
        "running_base_price_unit": "USD/carton kilometer"
    }
}
from services.haulage_freight_rate.models.haulage_freight_rate_rule_sets import HaulageFreightRateRuleSet
def insert_south_america():
    for i, d in data.items():
        HaulageFreightRateRuleSet.create(distance=1, train_load_type = 'Wagon Load', commodity_class_type = 'default', base_price = float(d['base_price']), country_code = 'NA', currency = 'USD', base_price_unit = d['base_price_unit'], running_base_price = float(d['running_base_price']), running_base_price_unit = d['running_base_price_unit'], container_type = i)
        print('done')
    return