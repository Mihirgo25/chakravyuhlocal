DEFAULT_PERMISSIBLE_CARRYING_CAPACITY = 54.90

DESTINATION_TERMINAL_CHARGES_INDIA = 15

CONTAINER_TYPE_CLASS_MAPPINGS = {
    # 120 refer
    "standard": {"india": "Class LR-3", "vietnam": "3"},
    "refer": {"india": "Class 165", "vietnam": "3"},
    "open_top": {"india": "Class LR1", "vietnam": "2"},
    "open_side": {"india": "Class 120", "vietnam": "2"},
    "flat_rack": {"india": "Class 130A", "vietnam": "2"},
    "iso_tank": {"india": "Class 150", "vietnam": "2"},
}

WAGON_COMMODITY_MAPPING = {
    "Class 200": "BCACBM",
    "Class LR-3": "BRNA",
    "Class 165": "BTPGLN",
    "Class 145": "BOXNHL",
    "Class LR1": "BCXT",
    "Class 130A": "BCNA",
    "Class 150": "BCXT",
    "Class 120": "BTAP",
    "1": "BRNA",
    "2": "BTAP",
    "3": "BTPGLN",
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

CONTAINER_SIZE_WAGON_MAPPING = {}

DEFAULT_SERVICE_PROVIDER_ID = "5dc403b3-c1bd-4871-b8bd-35543aaadb36"

DEFAULT_MAX_WEIGHT_LIMIT = {"20": 18, "40": 30, "40HC": 32.5, "45HC": 32.68}

DEFAULT_HAULAGE_TYPE = "merchant"

DEFAULT_TRIP_TYPE = "one_way"

CONTAINER_SIZE_FACTORS = {"20": 1, "40": 1.1, "40HC": 1.15, "45HC": 1.2}

WEIGHT_LIMIT_CONSTANTS = {
    "upto_500km": {"upto_17_ton": 0.3636, "upto_23_ton": 0.4, "upto_28_ton": 0.4651},
    "upto_1000km": {"upto_17_ton": 0.3571, "upto_23_ton": 0.4, "upto_28_ton": 0.4651},
    "more_than_1000km": {
        "upto_17_ton": 0.3333,
        "upto_23_ton": 0.4,
        "upto_28_ton": 0.4651,
    },
}

COUNTRY_CURRENCY_CODE_MAPPING = {
    "india": "INR",
    "CN": "CNY",
    "US": "USD",
    "CA": "CAD",
    "MX": "MXN",
    "vietnam": "VND",
}

GLOBAL_FUEL_DATA_LINKS = [
    "https://www.globalpetrolprices.com/india/electricity_prices/"
]

CONTAINER_TO_WAGON_TYPE_MAPPING = {
    "standard": "2 axles",
    "refer": "2 axles",
    "open_top": "More than 2 axles",
    "open_side": "More than 2 axles",
    "flat_rack": "5 and 6 axles",
    "iso_tank": "3 and 4 axles",
}

CONTAINER_HANDLING_CHARGES = {
    "20": {
        "stuffed": {"warehouse_to_automobile": 23.00, "automobile_to_warehouse": 57.00},
        "empty": {"warehouse_to_automobile": 15.00, "automobile_to_warehouse": 37.00},
    },
    "40": {
        "stuffed": {"warehouse_to_automobile": 35.00, "automobile_to_warehouse": 85.00},
        "empty": {"warehouse_to_automobile": 23.00, "automobile_to_warehouse": 55.00},
    },
    "40HC": {
        "stuffed": {
            "warehouse_to_automobile": 53.00,
            "automobile_to_warehouse": 127.00,
        },
        "empty": {"warehouse_to_automobile": 34.00, "automobile_to_warehouse": 83.00},
    },
    # "45HC" : {"stuffed": {"warehouse_to_automobile": 23.00, "automobile_to_warehouse": 57.00}, "empty": {"warehouse_to_automobile": 15.00, "automobile_to_warehouse": 37.00}}
}

GENERAL_INFLATION_FACTOR = 1.76

VIETNAMESE_INFLATION_FACTOR = 1.76

CHARGE_LEVEL_MAPPING_VEITNAM = {}

USD_TO_VND = 23482.50

DEFAULT_ENVIRONMENT_PROTECTION_INDEX = 0.00543

DEFAULT_CLIMATE_CHANGE_FEE_INDEX = 0.00116

DEFAULT_NOISE_POLLUTION_FEE_INDEX = 0.00053

DEFAULT_INDIRECT_POLLUTION_FEE_INDEX = 0.00742

DEFAULT_POLLUTION_INDEX = 0.01454

DEFAULT_SAFTEY_INDEX = 0.97

DEFAULT_WEIGHT_INDEX = 0.25

AVERAGE_ENERGY_CONSUMPTION = 0.41

AVERAGE_GLOBAL_CO2_EMISSION = 104