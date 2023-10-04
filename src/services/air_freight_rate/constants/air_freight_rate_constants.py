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

CARGOAI_ACTIVE_ON_DISLIKE_RATE = True

PROCURE_NON_AVAILABLE_RATE_FROM_CARGOAI = True

SURCHARGE_SERVICE_PROVIDERS = [
'0b301989-9905-40a2-869a-eaff7ca2ca7e',
'4409296e-f087-46f5-a76a-35952058a2e8',
'36cee6fb-eeaf-4643-9db5-397544339635',
'536abfe7-eab8-4a43-a4c3-6ff318ce01b5'
]

COGOXPRESS = '536abfe7-eab8-4a43-a4c3-6ff318ce01b5'


SURCHARGE_NOT_ELIGIBLE_LINE_ITEM_MAPPINGS = {
    'bdef6da0-8353-4b9a-b422-550ebe9c2474':{'airlines':{'3a8dc0d2-2bb9-40f4-b9c4-993b6bf273e4','83af97eb-09a7-4a17-a3ca-561f0bbc0b6f'},'not_eligible_line_items':['AMS','EHAMS','HAMS']}
}

DEFAULT_NOT_APPLICABLE_LINE_ITEMS = ['EAMS','EHAMS','HAMS']


AIR_COVERAGE_USERS = [
    "f47788fe-85e8-4f86-a9d7-7c7902ea864a",
    "836a8d20-c273-485f-b787-c6b7bfe76f77",
    "2296510a-1693-4c38-9d41-1a2d6d50b823",
    "b26629b3-49c8-4874-a758-b733045cb45d",
]

AIR_LOCALS_COVERAGE_USERS = []


CRITICAL_AIRPORTS_INDIA_VIETNAM = [
    "676b663a-cab8-48dd-a6da-d28c6ee3f20c",
    "06b9cf22-74bf-496b-ab6d-8dcb67489233",
    "2f6f6dbc-c10b-4d1d-b9fd-e89298fb487c",
    "7391cac2-e8db-467f-a59b-574d01dd7e7c",
    "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
    "aeb6e88f-4379-4398-bf9e-18f91c78e1f3",
    "093f1fb6-feab-448a-a683-7dc7984734e0",
    "2b436d09-40a3-4c0e-a07a-ebb0db38f164",
    "a7da60eb-4f72-439c-b400-ac386b3d9d83",
]

IMPORTER_EXPORTER_ID_FOR_FREIGHT_FORCE = [
    "212204d5-147f-48e5-8ea4-dc102679e12a",
    "5ba5382f-4d1f-402b-9a86-d2ef0698d481",
    "5123cb97-a549-4d73-9fb4-f7731213b910",
    "9528ad82-946d-4508-8771-a2c946a727af",
    "e5fa1021-5f79-4603-8906-3db8df40b894",
    "f5dde65d-018c-421d-9b9b-725c53f10cbf",
    "9df5bd09-70a3-4ae1-9fb0-a6cccb782ca9",
    "92634a7b-72d5-4abb-b160-bc037bf2b281",
    "88659e56-6422-43e2-90c3-7fda4a0551b2",
    "dce55557-0713-4011-87a9-7f4fc4862ad8",
    "4cc76d39-402a-4195-8da3-437116683756",
    "a2e3d5b4-8b55-45f2-8c00-ed3809cf1c80",
    "315ee0bb-711e-452a-aff7-a38e0f9ed721",
    "065de9b2-5889-4b15-97f3-49266c60d600",
    "a37f7f18-4a59-4dd4-8ed9-62c55ef2f360",
    "87298091-3d9f-40c6-a442-242abececde9",
    "a91fe507-e895-47de-9e03-e7b43d7a2b55",
    "00157356-950b-4b5f-8a3c-6c99958bdd5e",
    "02b01244-7a40-4186-a294-f5fa8ecdfbff",
    "304b60a9-c234-476d-a67f-830fca7adbc0",
    "b4b11c08-067c-4e07-be7f-44d37d8e0165",
    "c95ce242-aa6a-4a9c-bfa5-e45fb019ef58",
    "50956840-76f6-40c8-bae2-45505a7513ec",
    "b1e5ed3e-316e-4d88-9ad7-c3c217dd2d59",
    "033e1599-e0c8-43e1-b2e5-7c3158ead41a",
    "d7c56da8-f268-4966-a853-dc773613804a",
    "23b0924c-f65c-4461-9d03-efadf8b87f51",
    "4ea84fb0-d83e-4494-afce-b1a4f9f60cd1",
    "ed81362c-078d-4be0-8630-4b2e110a8434",
    "a68a77c4-2a9d-4066-874c-163fa028aa03",
    "e6b9b526-843d-4afa-8537-a31914350318",
    "b2de244e-fe8a-4893-bf8c-b1f4bdc74355",
    "2082a7b8-7ffc-45ca-88e4-770e97327a9c",
    "8ab7d54d-92a1-4df0-9921-2251464c143a",
    "5bf68f32-6c70-40f7-b5c7-6e77fd0176ef",
    "e34b3287-19c8-4f10-9ab5-150bfd181702",
    "d117a77e-0e0a-4b67-9797-dd9ca6dd3bc0",
    "fc3abe04-c6a2-414b-9d4e-324c855e9e32",
    "adb15c1f-c44a-49c1-8e6e-dda89128f12a",
    "da696e87-f119-40ca-95d3-9ec5eccf9bb4",
    "27e83ea1-a6b2-4ba4-9322-f92b516334a3",
    "44a23dd8-8121-4aa8-99be-009e1bc62cc9",
    "d4135cb3-0325-4d5f-b56f-5382f64cd2b8",
    "8105c837-6bff-4f5e-9728-5d6c42b9852c",
    "3353ede9-43b5-465a-9a01-4995a75913d3",
    "9843e0c8-6c20-4e0b-9902-a4feff1f6db8",
    "370ed734-2df6-415d-b1cb-50bdb2b0b056",
    "a87cdf6e-0170-44ec-b7e4-228c6370ac0d",
    "04e3b582-6914-48af-a201-5df3e6a971bf",
    "9eb4b614-ab5b-47be-af6a-cf83dee0900a",
    "48501f00-b810-4ae6-9d7d-47d2fc4b30ed",
    "7e3be863-c2d6-400c-8fc6-67cb8945e747",
    "995aeb83-d707-42df-9e7c-12ab7c8c9b02",
    "75d915d2-24c3-4d03-8ce7-23b494da5972",
]

AIR_LOCAL_COVERAGE_USERS = []