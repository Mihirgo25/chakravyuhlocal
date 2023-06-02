DEFAULT_PERMISSIBLE_CARRYING_CAPACITY = 54.90

DESTINATION_TERMINAL_CHARGES_INDIA = 15

CONTAINER_TYPE_CLASS_MAPPINGS = {
    # 120 refer
    "standard": ["Class LR-3"],
    "refer": ["Class 165","Class 200"],
    "open_top": ["Class LR1"],
    "open_side": ["Class 120", "Class 170"],
    "flat_rack": ["Class 130A"],
    "iso_tank": ["Class 150"],
}

WAGON_COMMODITY_MAPPING = {
    "Class 200": "BCACBM",
    "Class LR-3": "BRNA",
    "Class 165": "BTPGLN",
    "Class 145": "BOXNHL",
    "Class LR1": "BCXT",
    "Class 130A": "BCNA",
    "Class 150": "BCXT",
    "Class 120": "BTAP"
}


WAGON_CONTAINER_TYPE_MAPPINGS = {
    "standard": [
        "BCX",
        "BCXC",
        "BCXR",
        "BCXT",
        "BCXN",
        "BCN",
        "BCNA",
        "BCNAHS",
        "BCNHL",
        "BCNAHS",
    ],
    "refer": [],
    "open_top": ["BOXNHL", "BOXNHS", "BOXNS", "BOY"],
    "open_side": ["BOBYN", "BOBSN", "BCFC", "BOBRN"],
    "flat_rack": ["BRNA", "BRNA-EUR", "BFNS", "BFNSM1", "BFNSM"],
    "iso_tank": ["BTNP", "BTAP", "BTALN", "BTPGLN", "BTCS"],
}


WAGON_MAPPINGS = {
    "BTPGLN": [
        {"permissable_carrying_capacity": 55.5},
        {"number_of_wagons": 60},
        {"container_size": "40"},
    ],
    "BRNA": [
        {"permissable_carrying_capacity": 55.5},
        {"number_of_wagons": 26},
        {"container_size": "20"},
    ],
    "BCACBM": [
        {"permissable_carrying_capacity": 55.5},
        {"number_of_wagons": 58},
        {"container_size": "40"},
    ],
    "BCX": [
        {"permissable_carrying_capacity": 55.5},
        {"number_of_wagons": 58},
        {"container_size": "40"},
    ],
    "BCXC": [
        {"permissable_carrying_capacity": 55.5},
        {"number_of_wagons": 58},
        {"container_size": "40"},
    ],
    "BCXR": [
        {"permissable_carrying_capacity": 55.5},
        {"number_of_wagons": 58},
        {"container_size": "40"},
    ],
    "BCXT": [
        {"permissable_carrying_capacity": 55.5},
        {"number_of_wagons": 58},
        {"container_size": "40"},
    ],
    "BCXN": [
        {"permissable_carrying_capacity": 55.5},
        {"number_of_wagons": 58},
        {"container_size": "40"},
    ],
    "BCN": [
        {"permissable_carrying_capacity": 58.0},
        {"number_of_wagons": 43},
        {"container_size": "20"},
    ],
    "BCNA": [
        {"permissable_carrying_capacity": 58.8},
        {"number_of_wagons": 43},
        {"container_size": "20"},
    ],
    "BCNAHS": [
        {"permissable_carrying_capacity": 58.8},
        {"number_of_wagons": 43},
        {"container_size": "20"},
    ],
    "BOXNHA": [
        {"permissable_carrying_capacity": 60.1},
        {"number_of_wagons": 43},
        {"container_size": "20"},
    ],
    "BOXN": [
        {"permissable_carrying_capacity": 58},
        {"number_of_wagons": 58},
        {"container_size": "40"},
    ],
    "BOXNHS": [
        {"permissable_carrying_capacity": 58},
        {"number_of_wagons": 58},
        {"container_size": "40"},
    ],
    "BOI": [
        {"permissable_carrying_capacity": 58},
        {"number_of_wagons": 58},
        {"container_size": "40"},
    ],
    "BRS": [
        {"permissable_carrying_capacity": 58},
        {"number_of_wagons": 58},
        {"container_size": "40"},
    ],
    "BRH": [
        {"permissable_carrying_capacity": 58},
        {"number_of_wagons": 58},
        {"container_size": "40"},
    ],
    "BRN": [
        {"permissable_carrying_capacity": 58},
        {"number_of_wagons": 58},
        {"container_size": "40"},
    ],
    "BOBS": [
        {"permissable_carrying_capacity": 58},
        {"number_of_wagons": 58},
        {"container_size": "40"},
    ],
    "BOBSN": [
        {"permissable_carrying_capacity": 58},
        {"number_of_wagons": 58},
        {"container_size": "40"},
    ],
    "BOBX": [
        {"permissable_carrying_capacity": 58},
        {"number_of_wagons": 58},
        {"container_size": "40"},
    ],
    "BOBY": [
        {"permissable_carrying_capacity": 58},
        {"number_of_wagons": 58},
        {"container_size": "40"},
    ],
    "BOBYN": [
        {"permissable_carrying_capacity": 58},
        {"number_of_wagons": 58},
        {"container_size": "40"},
    ],
    "BOX": [
        {"permissable_carrying_capacity": 60},
        {"number_of_wagons": 58},
        {"container_size": "40"},
    ],
    "BOST": [
        {"permissable_carrying_capacity": 60},
        {"number_of_wagons": 58},
        {"container_size": "40"},
    ],
    "BOBR": [
        {"permissable_carrying_capacity": 60},
        {"number_of_wagons": 58},
        {"container_size": "40"},
    ],
    "BTNP": [
        {"permissable_carrying_capacity": 60},
        {"number_of_wagons": 58},
        {"container_size": "40"},
    ],
    "BTALN": [
        {"permissable_carrying_capacity": 60},
        {"number_of_wagons": 58},
        {"container_size": "40"},
    ],
    "BTPGLN": [
        {"permissable_carrying_capacity": 60},
        {"number_of_wagons": 58},
        {"container_size": "40"},
    ],
    "BTCS": [
        {"permissable_carrying_capacity": 60},
        {"number_of_wagons": 58},
        {"container_size": "40"},
    ],
    "BTPN": [
        {"permissable_carrying_capacity": 54.28},
        {"number_of_wagons": 47},
        {"container_size": "20"},
    ],
    "BTAP": [
        {"permissable_carrying_capacity": 54.28},
        {"number_of_wagons": 47},
        {"container_size": "20"},
    ],
    "BCNAHS": [
        {"permissable_carrying_capacity": 56.73},
        {"number_of_wagons": 43},
        {"container_size": "20"},
    ],
    "BRNA-EUR": [
        {"permissable_carrying_capacity": 56.73},
        {"number_of_wagons": 18},
        {"container_size": "20"},
    ],
    "BFNSM": [
        {"permissable_carrying_capacity": 56.73},
        {"number_of_wagons": 68},
        {"container_size": "40HC"},
    ],
    "BOXNHL": [
        {"permissable_carrying_capacity": 71.05},
        {"number_of_wagons": 58},
        {"container_size": "40"},
    ],
    "BOXNHS": [
        {"permissable_carrying_capacity": 58.08},
        {"number_of_wagons": 58},
        {"container_size": "40"},
    ],
    "BCNHL": [
        {"permissable_carrying_capacity": 70.8},
        {"number_of_wagons": 58},
        {"container_size": "40"},
    ],
    "BOXNS": [
        {"permissable_carrying_capacity": 80.15},
        {"number_of_wagons": 59},
        {"container_size": "40"},
    ],
    "BOY": [
        {"permissable_carrying_capacity": 70.89},
        {"number_of_wagons": 52},
        {"container_size": "40"},
    ],
    "BRNA": [
        {"permissable_carrying_capacity": 57.7},
        {"number_of_wagons": 43},
        {"container_size": "20"},
    ],
    "BFNS": [
        {"permissable_carrying_capacity": 70.8},
        {"number_of_wagons": 54},
        {"container_size": "40"},
    ],
}

CONTAINER_SIZE_WAGON_MAPPING = {}

DEFAULT_SERVICE_PROVIDER_ID = '5dc403b3-c1bd-4871-b8bd-35543aaadb36'

DEFAULT_MAX_WEIGHT_LIMIT = {
    '20': 18,
    '40': 30,
    '40HC':32.5,
    '45HC': 32.68
}

DEFAULT_HAULAGE_TYPE = 'merchant'

DEFAULT_TRIP_TYPE = 'one_way'

CONTAINER_SIZE_FACTORS = {
    '20': 1,
    '40': 1.1,
    '40HC': 1.15,
    '45HC': 1.2
}

weight_limit_constants = {'upto_500km':{'upto_17_ton':0.3636, 'upto_23_ton':0.4, 'upto_28_ton':0.4651}
                            ,'upto_1000km':{'upto_17_ton':0.3571, 'upto_23_ton':0.4, 'upto_28_ton':0.4651}
                            ,'more_than_1000km':{'upto_17_ton':0.3333, 'upto_23_ton':0.4, 'upto_28_ton':0.4651}
}

COUNTRY_CURRENCY_CODE_MAPPING = {
    'IN': 'INR',
    'CN': 'CNY',
    'US': 'USD',
    'CA': 'CAD',
    'MX': 'MXN',
    'VN': 'VND'
}

GLOBAL_FUEL_DATA_LINKS = ['https://www.globalpetrolprices.com/india/electricity_prices/']

CONTAINER_TO_WAGON_TYPE_MAPPING = {
    'standard': '2 axles',
    'refer': '2 axles',
    'open_top': 'More than 2 axles',
    'open_side': 'More than 2 axles',
    'flat_rack': '5 and 6 axles',
    'iso_tank': '3 and 4 axles'
}

CONTAINER_HANDLING_CHARGES = {
    "20" : {"stuffed": {"warehouse_to_automobile": 23.00, "automobile_to_warehouse": 57.00}, "empty": {"warehouse_to_automobile": 15.00, "automobile_to_warehouse": 37.00}},
    "40" : {"stuffed": {"warehouse_to_automobile": 35.00, "automobile_to_warehouse": 85.00}, "empty": {"warehouse_to_automobile": 23.00, "automobile_to_warehouse": 55.00}},
    "40HC" : {"stuffed": {"warehouse_to_automobile": 53.00, "automobile_to_warehouse": 127.00}, "empty": {"warehouse_to_automobile": 34.00, "automobile_to_warehouse": 83.00}},
    # "45HC" : {"stuffed": {"warehouse_to_automobile": 23.00, "automobile_to_warehouse": 57.00}, "empty": {"warehouse_to_automobile": 15.00, "automobile_to_warehouse": 37.00}}
}

GENERAL_INFLATION_FACTOR = 1.76

VIETNAMESE_INFLATION_FACTOR = 1.76

CHARGE_LEVEL_MAPPING_VEITNAM = {
    
}