
from configs.global_constants import HAZ_CLASSES
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

DEFAULT_SERVICE_PROVIDER_ID = "5dc403b3-c1bd-4871-b8bd-35543aaadb36"

DEFAULT_MAX_WEIGHT_LIMIT = {"20": 18, "40": 30, "40HC": 32.5, "45HC": 32.68}

DEFAULT_HAULAGE_TYPE = "merchant"

DEFAULT_TRIP_TYPE = "one_way"

DEFAULT_RATE_TYPE = 'market_place'

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
        "stuffed": {
            "warehouse_to_automobile": 23.00,
            "automobile_to_warehouse": 57.00,
        },
        "empty": {
            "warehouse_to_automobile": 15.00,
            "automobile_to_warehouse": 37.00,
        },
    },
    "40": {
        "stuffed": {
            "warehouse_to_automobile": 35.00,
            "automobile_to_warehouse": 85.00,
        },
        "empty": {
            "warehouse_to_automobile": 23.00,
            "automobile_to_warehouse": 55.00,
        },
    },
    "40HC": {
        "stuffed": {
            "warehouse_to_automobile": 53.00,
            "automobile_to_warehouse": 127.00,
        },
        "empty": {
            "warehouse_to_automobile": 34.00,
            "automobile_to_warehouse": 83.00,
        },
    },
    "45HC": {
        "stuffed": {
            "warehouse_to_automobile": 57.00,
            "automobile_to_warehouse": 145.00,
        },
        "empty": {
            "warehouse_to_automobile": 39.00,
            "automobile_to_warehouse": 97.00,
        },
    },
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

GENERALIZED_WEIGHT_OF_ECONOMY = 0.25

EUROPE_INFLATION_RATES = [0.0018,0.0103,0.0185,0.0111,0.0048,0.0164,0.0522]

LOCATION_PAIR_HIERARCHY = {
    'pincode:pincode' : 1,
    'seaport:seaport' : 2,
    'pincode:seaport' : 3,
    'seaport:pincode' : 4,
    'pincode:city' : 5,
    'seaport:city' : 6,
    'city:pincode' : 7,
    'city:seaport' : 8,
    'city:city' : 9,
    'pincode:country' : 10,
    'seaport:country' : 11,
    'country:pincode' : 12,
    'country:seaport' : 13,
    'city:country' : 14,
    'country:city' : 15,
    'country:country' : 16,

}
HAULAGE_FREIGHT_TYPES = ['carrier', 'merchant']

TRANSPORT_MODES = ['rail', 'barge', 'trailer']

TRAILER_TYPES = ['flat_bed', 'semi_flat_bed', 'xl_bed']

TRIP_TYPES = ['one_way', 'round_trip']

COMMODITY = ['general', 'dangerous', 'temp_controlled']

HAULAGE_CONTAINER_TYPE_COMMODITY_MAPPINGS = {
    'standard':  [None] + HAZ_CLASSES + COMMODITY,
    'refer':  [None] + COMMODITY,
    'open_top':  [None] + COMMODITY,
    'open_side':  [None] + COMMODITY,
    'flat_rack':  [None] + COMMODITY,
    'iso_tank':  [None] + HAZ_CLASSES + COMMODITY,
    'conventional_end_opening':  COMMODITY,
    'high_cube_end_opening':  COMMODITY,
    'side_access':  COMMODITY,
    'refrigerated':  COMMODITY,
    'flat_rack_collapsible':  COMMODITY,
    'platform':  COMMODITY,
    'tank':  COMMODITY,
    'high_cube_refrigerated':  COMMODITY,
    'ss_tank':  COMMODITY,
    'ms_tank':  COMMODITY,
    'ss_volve_tank':  COMMODITY,
    'ms_volve_tank':  COMMODITY,
    'ss_blank_tank':  COMMODITY,
    'ms_blank_tank':  COMMODITY,
    'ss_hc_tank':  COMMODITY,
    'ms_hc_tank':  COMMODITY,
    'ss_blank_hc_tank':  COMMODITY,
    'ms_blank_hc_tank':  COMMODITY,
    'ss_normal_tank':  COMMODITY,
    'ms_normal_tank':  COMMODITY
  }

RATE_TYPES = ['market_place', 'cogo_assured', 'promotional', 'spot_booking']

FEEDBACK_SOURCES = ['spot_search', 'checkout']

POSSIBLE_FEEDBACKS = ['unsatisfactory_rate']

FEEDBACK_TYPES = ['liked', 'disliked']

REQUEST_SOURCES = ['spot_search']

SOUTH_AMERICA_INFLATION_FACTOR = 0.89

PREDICTED_PRICE_SERVICE_PROVIDER = "5dc403b3-c1bd-4871-b8bd-35543aaadb36"

PREDICTION_HAULAGE_TYPE = 'merchant'

HAULAGE_PREDICTION_TRANSPORT_MODES = ['rail']

TRAILER_PREDICTION_TRANSPORT_MODES = ['trailer']

PREDICTION_TRAILER_TYPE = 'flat_bed'