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


AIR_COVERAGE_USERS = {
    1: "f47788fe-85e8-4f86-a9d7-7c7902ea864a",
    2: "836a8d20-c273-485f-b787-c6b7bfe76f77",
    3: "2296510a-1693-4c38-9d41-1a2d6d50b823",
    4: "b26629b3-49c8-4874-a758-b733045cb45d",
}

CRITICAL_AIRPORTS_MAPPINGS=[
    { "origin_airport_id": "ff07a2bc-2800-4760-9f58-2e3a6b4950d4", "destination_airport_id": "06b9cf22-74bf-496b-ab6d-8dcb67489233", "airline_id": "dbd3feb3-007a-4e24-873a-bc6e5e43254d" }, #1
    { "origin_airport_id": "ff6d4fc7-bf56-44e3-a316-60982fe69998", "destination_airport_id": "06b9cf22-74bf-496b-ab6d-8dcb67489233", "airline_id": "3a18959b-f657-495e-84b2-f94ec82b65ba" }, #2
    { "origin_airport_id": "bf8f98d8-7387-4830-8186-ea0e7ab8bc6c", "destination_airport_id": "06b9cf22-74bf-496b-ab6d-8dcb67489233", "airline_id": "cd0a5a97-add6-4387-9966-1011ec465951" }, #3
    { "origin_airport_id": "d48551a4-c8da-4fc1-ace1-7217a4fdc3b0", "destination_airport_id": "06b9cf22-74bf-496b-ab6d-8dcb67489233", "airline_id": "cd0a5a97-add6-4387-9966-1011ec465951" }, #4
    { "origin_airport_id": "b6503b3e-529e-4333-8014-7d3408522876", "destination_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c", "airline_id": "5c1cc41e-bbee-4fb6-b4ca-fe2e9beb1351" }, #5
    { "origin_airport_id": "b6503b3e-529e-4333-8014-7d3408522876", "destination_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c", "airline_id": "b6ee9f34-d04e-47c5-b6c7-cb348eafdbbc" }, #6
    { "origin_airport_id": "34f857e3-ce05-444c-afeb-bb8b439823bf", "destination_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c", "airline_id": "83af97eb-09a7-4a17-a3ca-561f0bbc0b6f" }, #7
    { "origin_airport_id": "0b3e2140-4e9f-4091-b2e7-cc7dda9d6eef", "destination_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c", "airline_id": "db2122ff-c4a4-4553-8abf-41c3b8d89ed8" }, #8
    { "origin_airport_id": "fd81cd18-8fed-4d61-9fe2-909cd3204006", "destination_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c", "airline_id": "17c61123-c3b6-44c0-8bbb-13b748bacdaa" }, #9
    { "origin_airport_id": "304d3eeb-69fe-4ecc-9b7f-4f343609e54c", "destination_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c", "airline_id": "a35b88be-a01a-417a-809f-e1cd9503ca15" }, #10
    { "origin_airport_id": "304d3eeb-69fe-4ecc-9b7f-4f343609e54c", "destination_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c", "airline_id": "5c1cc41e-bbee-4fb6-b4ca-fe2e9beb1351" }, #11
    { "origin_airport_id": "ff6d4fc7-bf56-44e3-a316-60982fe69998", "destination_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c", "airline_id": "3a18959b-f657-495e-84b2-f94ec82b65ba" }, #12
    { "origin_airport_id": "f8b06480-e173-42ac-b328-dc63fc20797e", "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19", "airline_id": "60e927e1-fc9b-403f-af67-7b7530d75fdd" }, #13
    { "origin_airport_id": "b0e91cc5-419b-4587-9f52-f6225538ede3", "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19", "airline_id": "dbd3feb3-007a-4e24-873a-bc6e5e43254d" }, #14
    { "origin_airport_id": "d596574b-0e61-4249-bc11-877e3df2822f", "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19", "airline_id": "17c61123-c3b6-44c0-8bbb-13b748bacdaa" }, #15
    { "origin_airport_id": "2fc877b2-063b-40fb-876c-283da8be9cf2", "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19", "airline_id": "83af97eb-09a7-4a17-a3ca-561f0bbc0b6f" }, #16
    { "origin_airport_id": "9cedff5e-86df-4706-9a62-5a06e4516a85", "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19", "airline_id": "b6ee9f34-d04e-47c5-b6c7-cb348eafdbbc" }, #17
    { "origin_airport_id": "9cedff5e-86df-4706-9a62-5a06e4516a85", "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19", "airline_id": "e942211b-f46f-4a07-9756-626377218d1d" }, #18
    { "origin_airport_id": "9cedff5e-86df-4706-9a62-5a06e4516a85", "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19", "airline_id": "6352cdbc-17dc-4ae8-88a1-9ebd2797fb7c" }, #19
    { "origin_airport_id": "8f7aed1e-32fd-45bc-9d30-d0246b0b31c5", "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19", "airline_id": "eddc9ad8-62f6-4445-bb37-4fce5d284ed1" }, #20
    { "origin_airport_id": "8f7aed1e-32fd-45bc-9d30-d0246b0b31c5", "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19", "airline_id": "e942211b-f46f-4a07-9756-626377218d1d" }, #21
    { "origin_airport_id": "465663fe-166a-4d20-a4ad-e1225b17bc3c", "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19", "airline_id": "3a18959b-f657-495e-84b2-f94ec82b65ba" }, #22
    { "origin_airport_id": "465663fe-166a-4d20-a4ad-e1225b17bc3c", "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19", "airline_id": "ce23e109-1770-4cbd-8703-bdb15f540ad9" }, #23
    { "origin_airport_id": "1ca10ec0-bd12-47c7-8a84-55898a4a88d0", "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19", "airline_id": "95f155aa-f388-4d55-af79-0d412b9cb138" }, #24
    { "origin_airport_id": "057adc95-4cff-4906-8644-c248b73512f3", "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19", "airline_id": "5f42585f-00cf-4d24-8a15-4baecfe9605e" }, #25
    { "origin_airport_id": "307fe7ca-763e-4350-b550-fd72fd5284e8", "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19", "airline_id": "eddc9ad8-62f6-4445-bb37-4fce5d284ed1" }, #26
    { "origin_airport_id": "0d674a4f-2395-4720-80fe-b5fc3847b16a", "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19", "airline_id": "ce23e109-1770-4cbd-8703-bdb15f540ad9" }, #27
    { "origin_airport_id": "0d674a4f-2395-4720-80fe-b5fc3847b16a", "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19", "airline_id": "e942211b-f46f-4a07-9756-626377218d1d" }, #28
    { "origin_airport_id": "0d674a4f-2395-4720-80fe-b5fc3847b16a", "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19", "airline_id": "df841d5e-28bc-4827-856d-654c66302b9d" }, #29
    { "origin_airport_id": "2b436d09-40a3-4c0e-a07a-ebb0db38f164", "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19", "airline_id": "06fe4d7a-55c2-4fc8-be74-cb4fc9499664" }, #30
    { "origin_airport_id": "f616faa5-baa5-4c5f-87a8-78d9609fd99f", "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19", "airline_id": "2e6ff674-845a-4fe9-8d08-a55a934200b8" }, #31
    { "origin_airport_id": "f616faa5-baa5-4c5f-87a8-78d9609fd99f", "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19", "airline_id": "7e112a94-2c78-4a1e-bb56-634cb955b154" }, #32
    { "origin_airport_id": "f616faa5-baa5-4c5f-87a8-78d9609fd99f", "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19", "airline_id": "de1097ab-3879-4efc-9753-b778d5e007d4" }, #33
    { "origin_airport_id": "f616faa5-baa5-4c5f-87a8-78d9609fd99f", "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19", "airline_id": "41f7c435-572b-4b91-8520-07729fa74a01" }, #34
    { "origin_airport_id": "304d3eeb-69fe-4ecc-9b7f-4f343609e54c", "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19", "airline_id": "cd0a5a97-add6-4387-9966-1011ec465951" }, #35
    { "origin_airport_id": "304d3eeb-69fe-4ecc-9b7f-4f343609e54c", "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19", "airline_id": "8b517da3-7721-4d98-8b41-75566214f532" }, #36
    { "origin_airport_id": "304d3eeb-69fe-4ecc-9b7f-4f343609e54c", "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19", "airline_id": "de1097ab-3879-4efc-9753-b778d5e007d4" }, #37
    { "origin_airport_id": "4a068610-ded4-491b-b1ac-d9b8e6f760da", "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19", "airline_id": "41f7c435-572b-4b91-8520-07729fa74a01" }, #38
    { "origin_airport_id": "4a068610-ded4-491b-b1ac-d9b8e6f760da", "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19", "airline_id": "c6a0eded-f427-4d89-bd0c-0c468beec334" }, #39
    { "origin_airport_id": "4a068610-ded4-491b-b1ac-d9b8e6f760da", "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19", "airline_id": "de1097ab-3879-4efc-9753-b778d5e007d4" }, #40
    { "origin_airport_id": "4a068610-ded4-491b-b1ac-d9b8e6f760da", "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19", "airline_id": "1e512052-bb4e-4075-b5d9-61a3e1d5de5a" }, #41
    { "origin_airport_id": "4a068610-ded4-491b-b1ac-d9b8e6f760da", "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19", "airline_id": "2e6ff674-845a-4fe9-8d08-a55a934200b8" }, #42
    { "origin_airport_id": "ff6d4fc7-bf56-44e3-a316-60982fe69998", "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19", "airline_id": "a35b88be-a01a-417a-809f-e1cd9503ca15" }, #43
    { "origin_airport_id": "ff6d4fc7-bf56-44e3-a316-60982fe69998", "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19", "airline_id": "e942211b-f46f-4a07-9756-626377218d1d" }, #44
    { "origin_airport_id": "f066d1f2-7ec9-43b0-b330-d4624d29af0a", "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19", "airline_id": "b6ee9f34-d04e-47c5-b6c7-cb348eafdbbc" }, #45
    { "origin_airport_id": "f066d1f2-7ec9-43b0-b330-d4624d29af0a", "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19", "airline_id": "cd0a5a97-add6-4387-9966-1011ec465951" }, #46
    { "origin_airport_id": "f066d1f2-7ec9-43b0-b330-d4624d29af0a", "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19", "airline_id": "41f7c435-572b-4b91-8520-07729fa74a01" }, #47
    { "origin_airport_id": "7c0e83f1-cb4c-4e76-9693-abc943788237", "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19", "airline_id": "5f42585f-00cf-4d24-8a15-4baecfe9605e" }, #48
    { "origin_airport_id": "56b6da75-30fb-4137-ade7-eadd41950def", "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19", "airline_id": "de1097ab-3879-4efc-9753-b778d5e007d4" }, #49
    { "origin_airport_id": "9cedff5e-86df-4706-9a62-5a06e4516a85", "destination_airport_id": "aeb6e88f-4379-4398-bf9e-18f91c78e1f3", "airline_id": "b6ee9f34-d04e-47c5-b6c7-cb348eafdbbc" }, #50
    { "origin_airport_id": "0222992e-240a-490a-82ba-4ecfdb5c2df8", "destination_airport_id": "aeb6e88f-4379-4398-bf9e-18f91c78e1f3", "airline_id": "6e557d55-82df-43a1-b609-d613292bcbf7" }, #51
    { "origin_airport_id": "6ca1b22a-8f7f-4c2a-a5f1-fda1a3ad2de3", "destination_airport_id": "676b663a-cab8-48dd-a6da-d28c6ee3f20c", "airline_id": "b6ee9f34-d04e-47c5-b6c7-cb348eafdbbc" }, #52
    { "origin_airport_id": "f066d1f2-7ec9-43b0-b330-d4624d29af0a", "destination_airport_id": "676b663a-cab8-48dd-a6da-d28c6ee3f20c", "airline_id": "b6ee9f34-d04e-47c5-b6c7-cb348eafdbbc" }  #53
]