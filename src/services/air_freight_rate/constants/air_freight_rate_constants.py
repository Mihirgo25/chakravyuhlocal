AIR_STANDARD_VOLUMETRIC_WEIGHT_CONVERSION_RATIO = 166.67
DEFAULT_FACTOR = 0.89

MAX_CARGO_LIMIT = 10000000.0

REQUEST_SOURCES = ["spot_search", "shipment"]

AIR_TRADE_IMPORT_TYPE = "import"

AIR_STANDARD_COMMODITIES = ['general', 'perishable', 'live_animals', 'pharma']

AIR_HAZARDOUS_COMMODITIES = ['hazardous']

AIR_GENERAL_COMMODITY_TYPE =['all']

AIR_SPECIAL_CONSIDERATION_COMMODITY_TYPES = ['dangerous','temp_controlled', 'other_special']

AIR_TRADE_EXPORT_TYPE = "export"

AIR_EXPRESS_COMMODITIES = ['express']

AIR_IMPORTS_HIGH_DENSITY_RATIO = 0.835

AIR_IMPORTS_LOW_DENSITY_RATIO = 1.10

AIR_EXPORTS_HIGH_DENSITY_RATIO = 0.6

AIR_EXPORTS_LOW_DENSITY_RATIO = 1.2

MAX_CARGO_LIMIT = 10000000.0

COMMODITY = ["general", "special_consideration"]

TEMP_CONTROLLED_COMMODITY_SUB_TYPE=['active_general_pharma','active_chilled','active_ambient','active_frozen','passive_general_pharma','passive_chilled','passive_ambient','passive_frozen']

DANGEROUS_COMMODITY_SUB_TYPE = ['class_1.1',' class_1.2', 'class_1.3', 'class_1.4', 'class_1.5', 'class_1.6', 'class_2.1', 'class_2.2', 'class_2.3','class_3', 'class_4.1', 'class_4.3', 'class_5.1', 'class_5.2', 'class_6.1', 'class_6.2', 'class_7' 'class_8', 'class_9']


OTHER_SPECIAL_COMMODITY_SUB_TYPE = ['valuables', 'perishable' ,'fragile', 'others']

GENERAL_COMMODITY_SUB_TYPE=["all"]

COMMODITY_TYPE_CODES = ['AUP', 'PER', 'FSD', 'PES', 'VUP', 'PEM', 'PAN']

GENERAL_COMMODITY_SUB_TYPE_CODE = []

SPECIAL_CONSIDERATION_COMMODITY_SUB_TYPE_CODE = []

COMMODITY_TYPE = AIR_GENERAL_COMMODITY_TYPE + AIR_SPECIAL_CONSIDERATION_COMMODITY_TYPES

ALL_COMMODITY = COMMODITY + AIR_GENERAL_COMMODITY_TYPE + GENERAL_COMMODITY_SUB_TYPE + GENERAL_COMMODITY_SUB_TYPE_CODE + AIR_SPECIAL_CONSIDERATION_COMMODITY_TYPES + TEMP_CONTROLLED_COMMODITY_SUB_TYPE + OTHER_SPECIAL_COMMODITY_SUB_TYPE + DANGEROUS_COMMODITY_SUB_TYPE + SPECIAL_CONSIDERATION_COMMODITY_SUB_TYPE_CODE

COMMODITY_SUB_TYPE = GENERAL_COMMODITY_SUB_TYPE+DANGEROUS_COMMODITY_SUB_TYPE+TEMP_CONTROLLED_COMMODITY_SUB_TYPE+OTHER_SPECIAL_COMMODITY_SUB_TYPE

COMMODITIES=AIR_EXPRESS_COMMODITIES+AIR_STANDARD_COMMODITIES+AIR_HAZARDOUS_COMMODITIES

LOCAL_COMMODITIES = AIR_STANDARD_COMMODITIES + AIR_HAZARDOUS_COMMODITIES

TECHOPS_TASK_ABORT_REASONS = ["sid_cancelled/changed", "airport_currently_not_served"]

DEFAULT_SERVICE_PROVIDER_ID = "536abfe7-eab8-4a43-a4c3-6ff318ce01b5"

DEFAULT_SOURCED_BY_ID = "7f6f97fd-c17b-4760-a09f-d70b6ad963e8"

DEFAULT_PROCURED_BY_ID = "7f6f97fd-c17b-4760-a09f-d70b6ad963e8"

DEFAULT_LOCAL_AGENT_ID = '536abfe7-eab8-4a43-a4c3-6ff318ce01b5'

POSSIBLE_FEEDBACKS = [
    "unsatisfactory_rate",
    "unsatisfactory_destination_storage",
    "unpreferred_airlines",
]

REQUEST_SOURCES = ["spot_search", "shipment"]

FEEDBACK_SOURCES = ["spot_search", "checkout", "rate_sheet"]

FEEDBACK_TYPES = ["liked", "disliked"]

PRICE_TYPES = ["net_net", "all_in"]

COMMODITY = ["general", "special_consideration"]

PACKING_TYPE = ["pallet", "box", "crate", "loose"]

HANDLING_TYPE = ["stackable", "non_stackable"]

RATE_TYPES = ["market_place", "promotional", "consolidated", "cogo_assured", "general"]

DEFAULT_RATE_TYPE = "market_place"

DEFAULT_MODE = "manual"

AIR_OPERATION_TYPES = ["passenger", "freighter", "charter", "prime", "lean"]

EXPECTED_TAT = 2

ROLE_IDS_FOR_NOTIFICATIONS = [
    "70710ab2-0f80-4e12-a4f5-d75660c05315",
    "dcdcb3d8-4dca-42c2-ba87-1a54bc4ad7fb",
]

DEFAULT_AIRLINE_IDS = [
    "e942211b-f46f-4a07-9756-626377218d1d",
    "83af97eb-09a7-4a17-a3ca-561f0bbc0b6f",
    "3a8dc0d2-2bb9-40f4-b9c4-993b6bf273e4",
]

SLAB_WISE_CHANGE_FACTOR = 0.89

AIRLINE_IDS_WITH_CUSTOM_WEIGHT_SLABS = [
    "6e557d55-82df-43a1-b609-d613292bcbf7",
    "3aa76fac-6f7d-40bb-b15d-e6336b334c25",
    "7f7558bf-d370-45e7-bad3-2ffbb31e3081",
    "fdb31d6f-049b-4fee-8bd9-c943fbcba160",
    "e997f000-26c4-42dc-a432-824f80a91998",
    "eb130aeb-e21b-47dd-a35f-7e24991f8de3",
]

CUSTOM_WEIGHT_SLABS = [
    {"lower_limit": 0, 
     "upper_limit": 45
    },

    {"lower_limit": 45.1, 
     "upper_limit": 100
    },

    {"lower_limit": 100.1,
    "upper_limit": 250
    },

    {"lower_limit": 250.1, 
     "upper_limit": 500
    },
]

DEFAULT_WEIGHT_SLABS = [
    {"lower_limit": 0,
      "upper_limit": 45
    },

    {"lower_limit": 45.1, 
     "upper_limit": 100
    },

    {"lower_limit": 100.1, 
     "upper_limit": 300
    },
    
    {"lower_limit": 300.1, 
     "upper_limit": 500
    },
]

RATE_SOURCE_PRIORITIES = {
    "cargo_ai": 1,
    "manual": 1,
    "rate_sheet": 1,
    "freight_look": 10,
    "predicted": 11,
    "default": 100
}

DEFAULT_FACTORS_WEIGHT_SLABS=[
    {
        'lower_limit':0.0,
        'upper_limit':45,
        'tariff_price':0,
        'currency':'INR',
        'unit':'per_kg'
    },
    {
        'lower_limit':45.1,
        'upper_limit':100.0,
        'currency':'INR',
        'tariff_price':0,
        'unit':'per_kg'

        },
    {
        'lower_limit':100.1,
        'upper_limit':300.0,
        'currency':'INR',
        'tariff_price':0,
        'unit':'per_kg'

    },
    {
        'lower_limit':300.1,
        'upper_limit':500.0,
        'currency':'INR',
        'tariff_price':0,
        'unit':'per_kg'

    },{
        'lower_limit':500.1,
        'upper_limit':1000.0,
        'currency':'INR',
        'tariff_price':0,
        'unit':'per_kg'
    }
]

DEFAULT_AIRLINE_ID = '853f3c4c-af7f-4912-98a8-1515000bcd20'

CARGOAI_ACTIVE_ON_DISLIKE_RATE = False

PROCURE_NON_AVAILABLE_RATE_FROM_CARGOAI = True