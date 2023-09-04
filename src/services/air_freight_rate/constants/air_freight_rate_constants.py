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


DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL = ['FSC', 'CTS', 'MSC', 'PSS', 'AMS', 'SSC', 'AEDEM', 'AEDC', 'AMSNO', 'XRAY']

DEFAULT_APPLICABLE_LINE_ITEMS_ELECTRONIC = ['FSC', 'CTS', 'MSC', 'PSS', 'EAMS', 'SSC', 'AEDEM', 'AEDC', 'AMSNO', 'XRAY']

SURCHARGE_ELIGIBLE_LINE_ITEMS_MAPPING = {

    'e942211b-f46f-4a07-9756-626377218d1d':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_ELECTRONIC},
    '83af97eb-09a7-4a17-a3ca-561f0bbc0b6f':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_ELECTRONIC},
    '3a8dc0d2-2bb9-40f4-b9c4-993b6bf273e4':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_ELECTRONIC},
    '6e557d55-82df-43a1-b609-d613292bcbf7':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_ELECTRONIC},
    'c42e191e-81e7-40bc-87b2-5c1add86f65e':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_ELECTRONIC},
    '0a5802fb-4302-4160-8915-2275572412c8':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    'df841d5e-28bc-4827-856d-654c66302b9d':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_ELECTRONIC},
    'dbd3feb3-007a-4e24-873a-bc6e5e43254d':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    '63c8381e-b879-46c0-a908-49e4dad25867':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    'eb130aeb-e21b-47dd-a35f-7e24991f8de3':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_ELECTRONIC},
    '5f42585f-00cf-4d24-8a15-4baecfe9605e':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_ELECTRONIC},
    '17c61123-c3b6-44c0-8bbb-13b748bacdaa':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    '82b7e744-19b1-4b74-9721-fb68d15ff4d6':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    'cd0a5a97-add6-4387-9966-1011ec465951':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_ELECTRONIC},
    'b6ee9f34-d04e-47c5-b6c7-cb348eafdbbc':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_ELECTRONIC},
    '67af974c-596b-4709-9fde-e0955fe09a5c':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_ELECTRONIC},
    '60e927e1-fc9b-403f-af67-7b7530d75fdd':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    '3aa76fac-6f7d-40bb-b15d-e6336b334c25':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    'f08a946e-c14e-4451-8398-c14f8be97933':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_ELECTRONIC},
    'eddc9ad8-62f6-4445-bb37-4fce5d284ed1':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    '8b517da3-7721-4d98-8b41-75566214f532':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    '01216d9f-0b8e-442f-9ffa-c704d8925898':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_ELECTRONIC},
    '16d49e24-e7e7-46bc-a0b9-d57a88b6b5d3':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    'd3fa16fe-985e-4f67-944a-af9f668998e9':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    '95f155aa-f388-4d55-af79-0d412b9cb138':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    'a35b88be-a01a-417a-809f-e1cd9503ca15':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    '05b60693-2f45-43cd-8771-85d0adbde5e2':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    'c09226a6-802a-4677-8de3-a51333d00bab':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    'd0bd6e8d-a1cb-4ac1-bac8-b9e8385be05a':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    '9dcb7e37-b2ec-4b90-a147-9bfd5b5a0bd5':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_ELECTRONIC},
    '4bf070b3-887a-42b4-8db4-6b6e058fa160':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    # '33(null)'
    'e73711ed-aec7-4556-a293-418206a1192b':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    '0c346d67-7e7c-4958-ac86-86ed1d2e6b73':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    '8c825d3f-f41d-41fb-a563-7d764166b06d':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    '8eee9c31-fd68-4ef1-abd2-2fe5578cd73f':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_ELECTRONIC},
    '2e6ff674-845a-4fe9-8d08-a55a934200b8':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    '7f7558bf-d370-45e7-bad3-2ffbb31e3081':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    'db2122ff-c4a4-4553-8abf-41c3b8d89ed8':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    '0b367600-d282-4071-ae2c-79fc075bb9db':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_ELECTRONIC},
    'ce23e109-1770-4cbd-8703-bdb15f540ad9':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_ELECTRONIC},
    '4c1f69f5-8e19-40b5-999b-e20b1c498cee':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    'e9a8f35c-3b78-4904-bc0e-e01af2dcff48':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    'b6595f1c-eb97-4f88-9469-5d3e6294ba99':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    'b39e6a62-05b1-4d8c-9387-18c63234ac35':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_ELECTRONIC},
    'a37b48a8-63a5-4998-b18b-298e5db1b761':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    'd90ea6e1-5eb9-4bc4-825b-17ec1301ec48':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    'c84853bf-2fe9-4ba3-a436-e0c2e3bd6e16':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    'e422bb59-3074-422d-bf9c-51afe93cc968':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    'fc968c86-d3fa-43f2-a51a-1abcf29a5119':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    'b4855293-3061-4a3f-80aa-e0b162ba3986':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    'e8168aca-06b2-4e84-98ea-9fc072b22ae5':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    '0983c020-afd0-49d8-af64-c0e5fe4a5226':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    'ccc36df4-df58-4564-89b3-a5a9696c1055':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    'fec7c499-0f3c-42b4-bf5a-ff9fe0c879da':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    'd3a3f521-ebe8-4f6e-869b-e4004b5ccdbb':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    '3b246de6-ec89-4dcc-8616-26bc8eed03cc':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    '02b825d2-7f02-41d6-b30c-62fa80af2222':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    '92ba3d3b-bf31-44cd-91c5-7430221a4ae1':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    '9ed04b0a-5df4-413d-a2d8-e4c5a39a3f08':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    '9fd89682-c72e-4211-8b85-30778c992078':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    '0aaf9a9b-aeeb-4dec-a9fd-dcc145930d63':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    # '64(null)'
    '6352cdbc-17dc-4ae8-88a1-9ebd2797fb7c':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    'bcde4d86-b053-469b-b802-5c412aef6047':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    'b74f0b9f-529f-48e1-ac14-8cc45c4a5ae5':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    '9c07d7a7-7955-4f27-8e91-277d4c386fbb':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    '3c5425c7-0bc5-438b-9dfc-530de874c9d8':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    '1e512052-bb4e-4075-b5d9-61a3e1d5de5a':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    '4c62ac52-f9b9-47a4-8623-fca32101a46e':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL},
    # '72(null)'
    '12804c93-a745-4c8b-a296-0d4ebf89c25a':{'eligible_line_items':DEFAULT_APPLICABLE_LINE_ITEMS_MANUAL}
}