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

CRITICAL_AIRPORTS_INDIA_VIETNAM=[
  '676b663a-cab8-48dd-a6da-d28c6ee3f20c',
  '06b9cf22-74bf-496b-ab6d-8dcb67489233',
  '2f6f6dbc-c10b-4d1d-b9fd-e89298fb487c',
  '7391cac2-e8db-467f-a59b-574d01dd7e7c',
  'aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19',
  'aeb6e88f-4379-4398-bf9e-18f91c78e1f3',
  '093f1fb6-feab-448a-a683-7dc7984734e0',
  '2b436d09-40a3-4c0e-a07a-ebb0db38f164',
  'a7da60eb-4f72-439c-b400-ac386b3d9d83'
]
INDIA_CRITICAL_PORT_PAIR = [
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "2862bb66-1e8d-478a-9d70-ffc8d33442bf",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "307fe7ca-763e-4350-b550-fd72fd5284e8",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "efcee5fc-9945-428c-9ffa-f01eb1ab7c26",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "fd51f6b5-02a0-4699-908f-2bff0b9d5298",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "a4dfcaf2-f934-41b5-b171-34de45bae5d3",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "9d8baf58-0c62-4e15-81d8-bcd679cdfdba",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "1ca10ec0-bd12-47c7-8a84-55898a4a88d0",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "6e17397f-d2b7-49bc-bf3d-67460dae72ec",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "d596574b-0e61-4249-bc11-877e3df2822f",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "c6ba558f-8657-4190-b4b5-1f3ccb7963f6",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "b9af273a-b350-4f93-98ee-40af61de66bf",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "e4bd9193-0cd5-462b-80ff-07922e87dbc4",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "9d8baf58-0c62-4e15-81d8-bcd679cdfdba",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "bfc25605-e7e9-46b5-bd23-cc8c2d075ca4",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "d1f886f2-3f6e-49a4-98b0-f6e7e27b8693",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "487ab2d0-2d89-4975-b600-2d550af69d47",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "f12bb63f-220c-49a8-8726-695809305a23",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "25dfc1de-0f6a-4a4e-bc81-45f756b2e1ba",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "5a5256fe-c944-4f4f-a162-aa97db53736a",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "f8b06480-e173-42ac-b328-dc63fc20797e",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "34f56121-b53d-4c14-b7be-c0bda58dc645",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "214b2bee-e9ea-4075-8727-4e99859301f5",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "42203f6b-e2c4-46c9-bb4d-08eb549da401",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "cc9ee452-f352-470b-8b14-b868936fa7c8",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "cc618bf7-1d56-412c-96ad-1b1b9ccd05ac",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "fb526455-f141-4dd2-b19c-6b326736a4d4",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "ff6d4fc7-bf56-44e3-a316-60982fe69998",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "8fb67827-69b3-424b-9507-738ff3d8d8b1",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "c7bd04dd-90c2-433d-80d9-752fc21fc08a",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "7a9cac74-fb06-4e8b-b5df-3ad267484df2",
    },
    {
        "origin_airport_id": "676b663a-cab8-48dd-a6da-d28c6ee3f20c",
        "destination_airport_id": "641f000-af1a-4f26-9fd3-be0998918e71",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "d16363a4-58e5-418c-9a95-a281d706318b",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "ff6d4fc7-bf56-44e3-a316-60982fe69998",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "bb484324-b2ae-43ac-9be2-fcce4a31a58b",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "f12171f4-7f54-4148-9de2-b9821a37ebcd",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "2ca2d2a6-fd48-41a7-9cc3-248aec0bce7c",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "d2d390cd-6ed3-4123-b4da-dcaae75c3dcc",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "e2c4d20f-c1f3-4c5d-b656-9a37acff3b7d",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "e7580cd6-922d-4bea-b5b2-6c9d48565bd1",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "1830d9db-97f1-4594-b4d4-591d3fcb1306",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "34f857e3-ce05-444c-afeb-bb8b439823bf",
    },
    {
        "origin_airport_id": "cb2dec1a-0fdf-46ad-a87c-ac9381c59c6d",
        "destination_airport_id": "4c05b787-526f-4a1e-9c16-5cfa16e26f55",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "794a05ee-d4ff-4b88-8430-faa84860f1cf",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "6e17397f-d2b7-49bc-bf3d-67460dae72ec",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "4809815e-10e4-4540-91d0-cf238b40d28c",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "47acc6d3-9f51-4566-b94c-559ea794bec4",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "48d3f726-5fde-404f-9075-90a5346fdb95",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "fb526455-f141-4dd2-b19c-6b326736a4d4",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "95dd6ce5-545f-47f3-8a29-a5cac8c82ea8",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "0d674a4f-2395-4720-80fe-b5fc3847b16a",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "0b3e2140-4e9f-4091-b2e7-cc7dda9d6eef",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "2b436d09-40a3-4c0e-a07a-ebb0db38f164",
    },
    {
        "origin_airport_id": "676b663a-cab8-48dd-a6da-d28c6ee3f20c",
        "destination_airport_id": "62402abc-39e5-4cd3-8291-533c0488a35c",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "aed61856-3e0a-4fb8-99a5-019d636a1fc5",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "8f67e554-3e2a-44aa-a3f7-5147bfe47c9e",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "7a9cac74-fb06-4e8b-b5df-3ad267484df2",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "ecaa11cd-af11-4fed-8ea1-f3727ab8a480",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "fee57d11-8e5e-4114-ab26-e39a373be783",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "48d3f726-5fde-404f-9075-90a5346fdb95",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "d596574b-0e61-4249-bc11-877e3df2822f",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "8f7aed1e-32fd-45bc-9d30-d0246b0b31c5",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "9cedff5e-86df-4706-9a62-5a06e4516a85",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "234a3afc-8d2b-44bb-94d1-4228ed514594",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "f8b06480-e173-42ac-b328-dc63fc20797e",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "e2c4d20f-c1f3-4c5d-b656-9a37acff3b7d",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "d0d7fec0-afca-42a2-a193-2bd94857930f",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "6cb7e076-d067-436a-892a-8135ac3a8089",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "ccbecf6c-c6c5-4027-bbff-b4d491c99bf3",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "47acc6d3-9f51-4566-b94c-559ea794bec4",
    },
    {
        "origin_airport_id": "06b9cf22-74bf-496b-ab6d-8dcb67489233",
        "destination_airport_id": "df8386b9-ab99-4c72-8023-caa19d3978c0",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "f12bb63f-220c-49a8-8726-695809305a23",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "d00f9096-0d75-4abe-bf7b-3d48ece58a06",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "fc349dc1-0436-4e2d-b96e-4b171932396a",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "58147884-6245-46e1-9b25-a41a7feebf81",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "3b184f16-2b62-4045-96da-3ea5619d5ad7",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "3cf0cc2a-ccb6-45a9-ba04-8cef878cd44d",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "42203f6b-e2c4-46c9-bb4d-08eb549da401",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "cfeff113-8c17-413b-a77f-0183ed99b1c9",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "9cedff5e-86df-4706-9a62-5a06e4516a85",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "b206adad-a7e2-4736-8997-d3853ba56779",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "14c6883c-cb22-47a9-9171-40dd0634cdcb",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "09720a5b-8901-4a28-a602-451c98aba23a",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "bfe829b5-0f5d-433b-8935-de0d6231d027",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "90d0e415-40ed-4f82-af1e-d5cb78a18223",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "6cb7e076-d067-436a-892a-8135ac3a8089",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "d1f886f2-3f6e-49a4-98b0-f6e7e27b8693",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "c298f645-7d0a-44cb-845f-da7d85ac0e16",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "Minsk National Airport, Minsk, Belarus",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "ff07a2bc-2800-4760-9f58-2e3a6b4950d4",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "d00f9096-0d75-4abe-bf7b-3d48ece58a06",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "3a32b5e5-edda-431d-9956-84c95b0eb346",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "c7573ee6-b073-40a8-96f5-49ad6241ae64",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "e0893efe-35d7-4fd9-ae2e-55a377cda42b",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "b47634bb-e087-410b-acb9-03d621020102",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "e22ce0b0-c0c3-444b-b51a-dddebb8a4559",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "ecaa11cd-af11-4fed-8ea1-f3727ab8a480",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "1b957fc1-9403-461e-bd0c-a7a472cea987",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "8fb67827-69b3-424b-9507-738ff3d8d8b1",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "25dfc1de-0f6a-4a4e-bc81-45f756b2e1ba",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "057adc95-4cff-4906-8644-c248b73512f3",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "18f6da3f-9c15-4475-83d8-859a01f28b09",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "26e5a1d4-7e30-49a5-9a1e-d6ebfc3f31af",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "16784297-f0c9-4e31-8355-f2e01b880e02",
    },
    {
        "origin_airport_id": "cb2dec1a-0fdf-46ad-a87c-ac9381c59c6d",
        "destination_airport_id": "877eb98a-bf79-4e30-a97d-f91f88b78116",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "afa76d0b-96a4-47bb-9e9f-318609b70239",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "16784297-f0c9-4e31-8355-f2e01b880e02",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "0792048d-a583-49a9-a666-66cdd7a420bd",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "7c0e83f1-cb4c-4e76-9693-abc943788237",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "0222992e-240a-490a-82ba-4ecfdb5c2df8",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "c6ba558f-8657-4190-b4b5-1f3ccb7963f6",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "ccbecf6c-c6c5-4027-bbff-b4d491c99bf3",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "01132343-a452-435c-a3ca-112509f588e0",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "09720a5b-8901-4a28-a602-451c98aba23a",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "214b2bee-e9ea-4075-8727-4e99859301f5",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "5b5e3375-4b98-48a3-b1c4-e91201035f56",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "4a48439f-b370-40fd-aa2b-ab7a507b3860",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "f12171f4-7f54-4148-9de2-b9821a37ebcd",
    },
    {
        "origin_airport_id": "676b663a-cab8-48dd-a6da-d28c6ee3f20c",
        "destination_airport_id": "b0e91cc5-419b-4587-9f52-f6225538ede3",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "b206adad-a7e2-4736-8997-d3853ba56779",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "a4dfcaf2-f934-41b5-b171-34de45bae5d3",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "bb484324-b2ae-43ac-9be2-fcce4a31a58b",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "b47634bb-e087-410b-acb9-03d621020102",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "5a5256fe-c944-4f4f-a162-aa97db53736a",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "304d3eeb-69fe-4ecc-9b7f-4f343609e54c",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "093f1fb6-feab-448a-a683-7dc7984734e0",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "afa76d0b-96a4-47bb-9e9f-318609b70239",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "fee57d11-8e5e-4114-ab26-e39a373be783",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "465663fe-166a-4d20-a4ad-e1225b17bc3c",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "14c6883c-cb22-47a9-9171-40dd0634cdcb",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "90d0e415-40ed-4f82-af1e-d5cb78a18223",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "4a48439f-b370-40fd-aa2b-ab7a507b3860",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "fd81cd18-8fed-4d61-9fe2-909cd3204006",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "852c7ad2-1642-46de-ade6-629598f258d5",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "307fe7ca-763e-4350-b550-fd72fd5284e8",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "5b5e3375-4b98-48a3-b1c4-e91201035f56",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "cfeff113-8c17-413b-a77f-0183ed99b1c9",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "1ca10ec0-bd12-47c7-8a84-55898a4a88d0",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "2b436d09-40a3-4c0e-a07a-ebb0db38f164",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "1b10dd60-59bf-4ab9-8dc4-08425f745215",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "304d3eeb-69fe-4ecc-9b7f-4f343609e54c",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "0b3e2140-4e9f-4091-b2e7-cc7dda9d6eef",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "2862bb66-1e8d-478a-9d70-ffc8d33442bf",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "ff07a2bc-2800-4760-9f58-2e3a6b4950d4",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "a033e825-4f3f-4b85-a41c-9211ba5e7125",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "0792048d-a583-49a9-a666-66cdd7a420bd",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "4809815e-10e4-4540-91d0-cf238b40d28c",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "c298f645-7d0a-44cb-845f-da7d85ac0e16",
    },
    {
        "origin_airport_id": "676b663a-cab8-48dd-a6da-d28c6ee3f20c",
        "destination_airport_id": "90d0e415-40ed-4f82-af1e-d5cb78a18223",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "db5e07d9-8481-4039-8789-c31e590af58e",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "cc618bf7-1d56-412c-96ad-1b1b9ccd05ac",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "d2f25acf-6597-455a-86b0-26db9cc0cfe7",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "95dd6ce5-545f-47f3-8a29-a5cac8c82ea8",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "bfe829b5-0f5d-433b-8935-de0d6231d027",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "fd81cd18-8fed-4d61-9fe2-909cd3204006",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "30ad823b-9585-491f-b1dc-8057bd3deade",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "2fc877b2-063b-40fb-876c-283da8be9cf2",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "87d29a09-b88f-46e6-85b1-15a284389770",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "355f69fc-1e16-4bb7-87a9-95f72e574758",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "18f6da3f-9c15-4475-83d8-859a01f28b09",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "d2d390cd-6ed3-4123-b4da-dcaae75c3dcc",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "8f7aed1e-32fd-45bc-9d30-d0246b0b31c5",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "26e5a1d4-7e30-49a5-9a1e-d6ebfc3f31af",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "c7573ee6-b073-40a8-96f5-49ad6241ae64",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "3d14d63e-ad0c-476f-b6d3-4df77c7a72ef",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "01132343-a452-435c-a3ca-112509f588e0",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "0222992e-240a-490a-82ba-4ecfdb5c2df8",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "34f857e3-ce05-444c-afeb-bb8b439823bf",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "0d674a4f-2395-4720-80fe-b5fc3847b16a",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "c01f49e5-c692-4ec0-b7f1-6d908523f09e",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "30ad823b-9585-491f-b1dc-8057bd3deade",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "bfc25605-e7e9-46b5-bd23-cc8c2d075ca4",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "e4bd9193-0cd5-462b-80ff-07922e87dbc4",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "093f1fb6-feab-448a-a683-7dc7984734e0",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "34f56121-b53d-4c14-b7be-c0bda58dc645",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "3cf0cc2a-ccb6-45a9-ba04-8cef878cd44d",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "465663fe-166a-4d20-a4ad-e1225b17bc3c",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "ddb85f58-50d7-4fc8-a2bf-7a1f8e4da6d8",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "e22ce0b0-c0c3-444b-b51a-dddebb8a4559",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "58147884-6245-46e1-9b25-a41a7feebf81",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "fc349dc1-0436-4e2d-b96e-4b171932396a",
    },
    {
        "origin_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
        "destination_airport_id": "1f698639-e1f0-4303-b076-f60d99b31aa1",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "f8b06480-e173-42ac-b328-dc63fc20797e",
    },
    {
        "origin_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
        "destination_airport_id": "852c7ad2-1642-46de-ade6-629598f258d5",
    },
    {
        "origin_airport_id": "ff07a2bc-2800-4760-9f58-2e3a6b4950d4",
        "destination_airport_id": "06b9cf22-74bf-496b-ab6d-8dcb67489233",
    },
    {
        "origin_airport_id": "9cedff5e-86df-4706-9a62-5a06e4516a85",
        "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
    },
    {
        "origin_airport_id": "ff6d4fc7-bf56-44e3-a316-60982fe69998",
        "destination_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
    },
    {
        "origin_airport_id": "465663fe-166a-4d20-a4ad-e1225b17bc3c",
        "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
    },
    {
        "origin_airport_id": "307fe7ca-763e-4350-b550-fd72fd5284e8",
        "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
    },
    {
        "origin_airport_id": "ff6d4fc7-bf56-44e3-a316-60982fe69998",
        "destination_airport_id": "06b9cf22-74bf-496b-ab6d-8dcb67489233",
    },
    {
        "origin_airport_id": "0d674a4f-2395-4720-80fe-b5fc3847b16a",
        "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
    },
    {
        "origin_airport_id": "f066d1f2-7ec9-43b0-b330-d4624d29af0a",
        "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
    },
    {
        "origin_airport_id": "b0e91cc5-419b-4587-9f52-f6225538ede3",
        "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
    },
    {
        "origin_airport_id": "0b3e2140-4e9f-4091-b2e7-cc7dda9d6eef",
        "destination_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
    },
    {
        "origin_airport_id": "2b436d09-40a3-4c0e-a07a-ebb0db38f164",
        "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
    },
    {
        "origin_airport_id": "ff07a2bc-2800-4760-9f58-2e3a6b4950d4",
        "destination_airport_id": "06b9cf22-74bf-496b-ab6d-8dcb67489233",
    },
    {
        "origin_airport_id": "2fc877b2-063b-40fb-876c-283da8be9cf2",
        "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
    },
    {
        "origin_airport_id": "4a068610-ded4-491b-b1ac-d9b8e6f760da",
        "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
    },
    {
        "origin_airport_id": "f8b06480-e173-42ac-b328-dc63fc20797e",
        "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
    },
    {
        "origin_airport_id": "f616faa5-baa5-4c5f-87a8-78d9609fd99f",
        "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
    },
    {
        "origin_airport_id": "f066d1f2-7ec9-43b0-b330-d4624d29af0a",
        "destination_airport_id": "676b663a-cab8-48dd-a6da-d28c6ee3f20c",
    },
    {
        "origin_airport_id": "fd81cd18-8fed-4d61-9fe2-909cd3204006",
        "destination_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
    },
    {
        "origin_airport_id": "9cedff5e-86df-4706-9a62-5a06e4516a85",
        "destination_airport_id": "aeb6e88f-4379-4398-bf9e-18f91c78e1f3",
    },
    {
        "origin_airport_id": "7c0e83f1-cb4c-4e76-9693-abc943788237",
        "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
    },
    {
        "origin_airport_id": "d596574b-0e61-4249-bc11-877e3df2822f",
        "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
    },
    {
        "origin_airport_id": "057adc95-4cff-4906-8644-c248b73512f3",
        "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
    },
    {
        "origin_airport_id": "b6503b3e-529e-4333-8014-7d3408522876",
        "destination_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
    },
    {
        "origin_airport_id": "56b6da75-30fb-4137-ade7-eadd41950def",
        "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
    },
    {
        "origin_airport_id": "34f857e3-ce05-444c-afeb-bb8b439823bf",
        "destination_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
    },
    {
        "origin_airport_id": "1ca10ec0-bd12-47c7-8a84-55898a4a88d0",
        "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
    },
    {
        "origin_airport_id": "6ca1b22a-8f7f-4c2a-a5f1-fda1a3ad2de3",
        "destination_airport_id": "676b663a-cab8-48dd-a6da-d28c6ee3f20c",
    },
    {
        "origin_airport_id": "bf8f98d8-7387-4830-8186-ea0e7ab8bc6c",
        "destination_airport_id": "06b9cf22-74bf-496b-ab6d-8dcb67489233",
    },
    {
        "origin_airport_id": "304d3eeb-69fe-4ecc-9b7f-4f343609e54c",
        "destination_airport_id": "7391cac2-e8db-467f-a59b-574d01dd7e7c",
    },
    {
        "origin_airport_id": "304d3eeb-69fe-4ecc-9b7f-4f343609e54c",
        "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
    },
    {
        "origin_airport_id": "0222992e-240a-490a-82ba-4ecfdb5c2df8",
        "destination_airport_id": "aeb6e88f-4379-4398-bf9e-18f91c78e1f3",
    },
    {
        "origin_airport_id": "d48551a4-c8da-4fc1-ace1-7217a4fdc3b0",
        "destination_airport_id": "06b9cf22-74bf-496b-ab6d-8dcb67489233",
    },
    {
        "origin_airport_id": "8f7aed1e-32fd-45bc-9d30-d0246b0b31c5",
        "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
    },
    {
        "origin_airport_id": "ff6d4fc7-bf56-44e3-a316-60982fe69998",
        "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
    },
]

VIETNAM_CRITICAL_PORT_PAIRS = [{
        "origin_airport_id": "093f1fb6-feab-448a-a683-7dc7984734e0",
        "destination_airport_id": "9cedff5e-86df-4706-9a62-5a06e4516a85",
    },
    {
        "origin_airport_id": "a7da60eb-4f72-439c-b400-ac386b3d9d83",
        "destination_airport_id": "9cedff5e-86df-4706-9a62-5a06e4516a85",
    },
    {
        "origin_airport_id": "093f1fb6-feab-448a-a683-7dc7984734e0",
        "destination_airport_id": "ff6d4fc7-bf56-44e3-a316-60982fe69998",
    },
    {
        "origin_airport_id": "093f1fb6-feab-448a-a683-7dc7984734e0",
        "destination_airport_id": "b6cabdb3-8e42-4daa-ba3c-47eb084c8fb9",
    },
    {
        "origin_airport_id": "093f1fb6-feab-448a-a683-7dc7984734e0",
        "destination_airport_id": "ff07a2bc-2800-4760-9f58-2e3a6b4950d4",
    },
    {
        "origin_airport_id": "093f1fb6-feab-448a-a683-7dc7984734e0",
        "destination_airport_id": "4c05b787-526f-4a1e-9c16-5cfa16e26f55",
    },
    {
        "origin_airport_id": "093f1fb6-feab-448a-a683-7dc7984734e0",
        "destination_airport_id": "1ca10ec0-bd12-47c7-8a84-55898a4a88d0",
    },
    {
        "origin_airport_id": "2b436d09-40a3-4c0e-a07a-ebb0db38f164",
        "destination_airport_id": "b50e6829-6295-4537-9e9e-9f58af79a206",
    },
    {
        "origin_airport_id": "093f1fb6-feab-448a-a683-7dc7984734e0",
        "destination_airport_id": "b50e6829-6295-4537-9e9e-9f58af79a206",
    },
    {
        "origin_airport_id": "093f1fb6-feab-448a-a683-7dc7984734e0",
        "destination_airport_id": "d9eec918-8d19-4b1f-ac2d-61c9649c3165",
    },
    {
        "origin_airport_id": "093f1fb6-feab-448a-a683-7dc7984734e0",
        "destination_airport_id": "d2d390cd-6ed3-4123-b4da-dcaae75c3dcc",
    },
    {
        "origin_airport_id": "093f1fb6-feab-448a-a683-7dc7984734e0",
        "destination_airport_id": "234a3afc-8d2b-44bb-94d1-4228ed514594",
    },
    {
        "origin_airport_id": "093f1fb6-feab-448a-a683-7dc7984734e0",
        "destination_airport_id": "4a48439f-b370-40fd-aa2b-ab7a507b3860",
    },
    {
        "origin_airport_id": "093f1fb6-feab-448a-a683-7dc7984734e0",
        "destination_airport_id": "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19",
    },
     {
        "origin_airport_id": "a9b60faa-7c06-4248-ac6d-7c9cc5da614a",
        "destination_airport_id": "2b436d09-40a3-4c0e-a07a-ebb0db38f164",
    },
    {
        "origin_airport_id": "676b663a-cab8-48dd-a6da-d28c6ee3f20c",
        "destination_airport_id": "2b436d09-40a3-4c0e-a07a-ebb0db38f164",
    },
    {
        "origin_airport_id": "5a5256fe-c944-4f4f-a162-aa97db53736a",
        "destination_airport_id": "093f1fb6-feab-448a-a683-7dc7984734e0",
    },
    {
        "origin_airport_id": "4a48439f-b370-40fd-aa2b-ab7a507b3860",
        "destination_airport_id": "093f1fb6-feab-448a-a683-7dc7984734e0",
    },
    {
        "origin_airport_id": "9cedff5e-86df-4706-9a62-5a06e4516a85",
        "destination_airport_id": "093f1fb6-feab-448a-a683-7dc7984734e0",
    },
    {
        "origin_airport_id": "25dfc1de-0f6a-4a4e-bc81-45f756b2e1ba",
        "destination_airport_id": "093f1fb6-feab-448a-a683-7dc7984734e0",
    },
    {
        "origin_airport_id": "1ca10ec0-bd12-47c7-8a84-55898a4a88d0",
        "destination_airport_id": "093f1fb6-feab-448a-a683-7dc7984734e0",
    },
    {
        "origin_airport_id": "c298f645-7d0a-44cb-845f-da7d85ac0e16",
        "destination_airport_id": "093f1fb6-feab-448a-a683-7dc7984734e0",
    },
    {
        "origin_airport_id": "081b229d-fa5b-47ce-9591-6adabb48566e",
        "destination_airport_id": "093f1fb6-feab-448a-a683-7dc7984734e0",
    },
    ]
