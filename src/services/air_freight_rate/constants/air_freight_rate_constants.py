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
    "1719e23f-e03a-42e9-9613-948e66f3ac0e",
    "050a9e8f-6e47-4c66-981e-48e301a3aa5e",
    "afaf0e4c-8b27-452f-b96a-4c96e219ea9c",
    "b799444e-f7db-4111-990d-db642a362f7b",
    "e779dfeb-f1f3-48eb-92e9-294eee4311c1",
    "cba7277c-06d2-4e7b-b94c-3449422c0985",
    "ca2cdc51-85a6-40dd-a8fb-52a0b1d0a4ca",
    "ed81362c-078d-4be0-8630-4b2e110a8434",
    "ad2e7e43-445e-4c66-baf7-8349701f88cd",
    "987aad8f-35e0-4e93-937f-3b4f28cd180a",
    "1c3b5d8a-039f-4a58-893d-546ec384f38f",
    "ab952137-30c1-44a6-afda-1f092e949ddb",
    "35ab53ea-e1b7-4fc5-a3de-8bc135cf830b",
    "ea96349e-11d9-411f-bda1-481f37478409",
    "0369f941-5fab-4a94-9456-bbe38446c8a8",
    "5aed0c01-6811-4c7b-91d6-1e7655839db6",
    "7de7c540-1af8-424e-8b58-2072b0d1c79f",
    "27e83ea1-a6b2-4ba4-9322-f92b516334a3",
    "4defa5ef-b919-447b-a7be-416348369034",
    "e6b9b526-843d-4afa-8537-a31914350318",
    "58fa811c-d868-48a0-81e3-bf8b982a3648",
    "f33f02b5-d037-41b4-b878-91d8c15c9a89",
    "8593b809-4818-4e84-b0d0-9fc8763cfb44",
    "b4b11c08-067c-4e07-be7f-44d37d8e0165",
    "3353ede9-43b5-465a-9a01-4995a75913d3",
    "858b9d3b-0598-42c4-8dd1-446860b8ce7b",
    "e2a471a7-0c48-41d2-8d5f-79f6f8c675e8",
    "e1aad31f-4855-4e97-851d-2dd37f83e50f",
    "55f92d7b-0407-45d4-a9c3-0b98eb6d29c4",
    "d7c56da8-f268-4966-a853-dc773613804a",
    "037d2b54-5c93-44b8-8962-d86d65d45398",
    "9b8f4a87-5c94-4de1-a0da-4013b5f8a4d6",
    "069199e2-c031-484f-a478-547fbeee5857",
    "a9e0ca0e-b5eb-43b1-b0ea-d1e45385c2c6",
    "2ebf55b0-9273-4113-b952-c2d527e397c6",
    "87298091-3d9f-40c6-a442-242abececde9",
    "b95f054d-bede-4608-8202-b2ade9863b5a",
    "82160a58-d57d-4998-a72b-4b52cc367c84",
    "e27db015-a320-4f48-9b82-bce7d03a8a8b",
    "982076b8-9084-4bb6-ad91-43ab9ea9ad0c",
    "60648da8-5008-44a5-b4f2-eac0132af35c",
    "b001a42a-d3fe-414c-852c-8c003a0e7df5",
    "00b714cb-6c77-4c66-8899-bf9509de3810",
    "aaafba6e-30b1-4ef2-bfff-1b56b983c46e",
    "388489b7-396f-45d9-9549-bf75089df8f5",
    "7d2194f7-2a73-4ed2-ad79-bfe8fb0b9b05",
    "be410d95-17e2-43b8-a570-1a33c8730abe",
    "fa42b5ff-d530-424d-9990-125e2c5c0081",
    "7a32f2cc-ee7e-4ae5-82fb-5cba0993a953",
    "b13cf406-fefe-4f68-92e7-af40ed46fcbe",
    "fae14200-52a7-45c2-abfd-de4fb0408ce1",
    "92634a7b-72d5-4abb-b160-bc037bf2b281",
    "8ab7d54d-92a1-4df0-9921-2251464c143a",
    "304b60a9-c234-476d-a67f-830fca7adbc0",
    "bf70b638-fb28-49aa-93e7-abdd901cbed8",
    "0d6c3d48-c597-4355-b5ae-9686dc5c61d0",
    "23b0924c-f65c-4461-9d03-efadf8b87f51",
    "a2e3d5b4-8b55-45f2-8c00-ed3809cf1c80",
    "02b01244-7a40-4186-a294-f5fa8ecdfbff",
    "a87cdf6e-0170-44ec-b7e4-228c6370ac0d",
    "cd4cd4c6-9df5-4d8d-ad14-920631bc8e3a",
    "dce55557-0713-4011-87a9-7f4fc4862ad8",
    "9843e0c8-6c20-4e0b-9902-a4feff1f6db8",
    "7779f8f9-d200-43a1-b819-b865627b72aa",
    "a91fe507-e895-47de-9e03-e7b43d7a2b55",
    "428ccade-752f-4a7b-b2c3-d06a5f223124",
    "88659e56-6422-43e2-90c3-7fda4a0551b2",
    "d4135cb3-0325-4d5f-b56f-5382f64cd2b8",
    "2e8c8dcd-7bd5-4967-9cb0-dd66c26e5e77",
    "315ee0bb-711e-452a-aff7-a38e0f9ed721",
    "dcc076dd-9d00-412d-9ecb-6909f6d7767b",
    "b473018b-a148-4e76-9502-2d98e869ea42",
    "1c415f4b-6a1f-4484-8a8d-4324ac3b147c",
    "4b720e08-20a1-494d-8e53-7edfadfb85a6",
    "029090f6-5819-4e68-8c67-c47a4f5be4f4",
    "00157356-950b-4b5f-8a3c-6c99958bdd5e",
    "9528ad82-946d-4508-8771-a2c946a727af",
    "56428bc0-8596-4a9e-b438-90c8f18875f5",
    "5b7685a9-98a7-4003-99ee-8c53bbebae0b",
    "9313d06f-2f9a-4f20-b8c2-8a595e4f8ba9",
    "7670a85d-e6c3-4b8d-827d-1421e30e4074",
    "5d5321da-6325-4d7f-a372-405e8990019c",
    "5849e397-02b4-4480-a540-f3da54988ce5",
    "2596e959-7dd1-4f9e-83de-6f98a454d5d2",
    "31ee513c-699b-4081-a7b5-dd2c17884d77",
    "f0b66b98-1f53-4d48-b0f8-06ad7a4db195",
    "93b29d7e-607e-402a-aeab-7c961ff7fe2c",
    "36d05300-b9a5-4295-9141-745ba1f3ec8b",
    "d37e4e00-eeda-4c42-8cf6-80e8fdd36ee7",
    "84bc337e-a22f-4639-8226-848a2b0d9d14",
    "45b9fadb-a122-4e39-991b-d3d238101d3b",
    "81867f3b-af14-471e-a808-e7e2bc55460e",
    "f4c62bde-873f-4233-8da4-5991ed600e8d",
    "dda5ec52-287d-495b-8aa3-70082b54fe31",
    "ac81c65a-5f8a-4e10-81c8-a4567b43ac6c",
    "dbf36a8f-3855-480d-b2a5-70653f3f6a27",
    "9eb4b614-ab5b-47be-af6a-cf83dee0900a",
    "c4fb0288-718e-41cc-8322-e05e7ca6042a",
    "7ab928c2-e8be-4bea-8fac-b68e416b83ed",
    "adb15c1f-c44a-49c1-8e6e-dda89128f12a",
    "48501f00-b810-4ae6-9d7d-47d2fc4b30ed",
    "44a23dd8-8121-4aa8-99be-009e1bc62cc9",
    "2082a7b8-7ffc-45ca-88e4-770e97327a9c",
    "fc3abe04-c6a2-414b-9d4e-324c855e9e32",
    "17ffb1ef-b26d-4dfb-acd2-19209325d724",
    "787bab42-674e-4418-a1b3-c92d86c8454d",
    "9f032cd2-1eb1-4e57-b805-f07385fa47c1",
    "d117a77e-0e0a-4b67-9797-dd9ca6dd3bc0",
    "8225ebfb-c09d-4bfb-9f29-64b5c6692953",
    "c6702242-1b05-4170-8b54-47ad20f87d6d",
    "dde841a4-992b-48de-b05b-083f507a2419",
    "a71b1896-02fc-4607-8d38-57e418152e62",
    "d5e3638d-42c7-40da-984d-41b284d57b6b",
    "69d444a8-6daa-4767-83ec-4525a0507568",
    "a021cabb-37a9-4c1c-8e28-823a4861ebd8",
    "15bfdd7a-bbb2-4463-9b06-fb13f00e71f1",
    "76767a99-24f0-4ebc-a5cc-6e95a93f9d6b",
    "a70dee9b-7cf1-45c4-b7d1-a1d2e9b5c456",
    "5bb442dc-7e25-4680-a7ed-f2e64c98b40f",
    "95b77fac-797c-4480-8f0c-85c19c2327b5",
    "995aeb83-d707-42df-9e7c-12ab7c8c9b02",
    "192df4dc-3bc0-436c-afae-bb6a7f365999",
    "50956840-76f6-40c8-bae2-45505a7513ec",
    "e7bf05cd-b547-419e-b241-ba4f00a09b99",
    "c1e9f828-7d67-493f-aae8-b9da29d0e493",
    "6c2f4941-caf6-409e-b93f-0679f7996929",
    "437ac164-1bd0-451e-a3dc-dbe7a8140444",
    "23f0366a-b416-471b-9ef6-10087ba6b9e3",
    "60e43f27-fa6d-47bf-8f98-fee1b07211e0",
    "3633cda0-467e-4de1-96ef-41f51b1689e7",
    "b47fa6e6-0965-45aa-beef-791c6e64b424",
    "97f69186-634f-436c-970b-f5d04be174de",
    "63a37715-aee1-4cd8-a532-8a7f9e2300a0",
    "462f3365-c08e-4a2a-89f3-621bc1082de4",
    "f253f0c9-d9d1-4a4d-81c8-b7f614a2e90a",
    "bfd2cbf3-62cd-4ca5-b932-2305c6052c7f",
    "5097765f-3d9f-4f7e-a0aa-143194347643",
    "75d915d2-24c3-4d03-8ce7-23b494da5972",
    "f5f27d78-37ae-4aa4-8778-632cec030232",
    "49613cd5-2af0-42e7-9e0e-7f8a26ec7a6f",
    "92274c0e-c6fb-4c56-b9b5-17a4a4aaf161",
    "c7bf0bf0-5b27-4602-9069-6e7844bd3674",
    "44bc84ce-7506-417e-8e5f-cb31f484fb9b",
    "5876e0c1-c08b-442a-9103-73ef2a6133b1",
]

IMPORTER_EXPORTER_ID_FOR_ENTERPRISE_SALES = [
    "31b05525-0168-429a-9754-65ec63586b9b",
    "c4e1fc14-994c-4454-a7a7-46585521fb81",
    "e5fa1021-5f79-4603-8906-3db8df40b894",
    "a68a77c4-2a9d-4066-874c-163fa028aa03",
    "eb60c2fa-e733-41d1-8892-a3fb25d5fa6b",
    "65f380e2-c1e1-4dcf-9b93-32f587c81bd8",
    "a829a9a9-7118-4bda-a321-a2c943794102",
    "d05c3ca3-7bb0-4c08-86be-67a385473a69",
    "6bd47094-5c33-402c-9824-8781978b7097",
    "4ea84fb0-d83e-4494-afce-b1a4f9f60cd1",
    "9df5bd09-70a3-4ae1-9fb0-a6cccb782ca9",
    "0ce2641c-ded8-4cfa-bbd2-a6e6566e4332",
    "1e3ed3f5-da62-4c81-bbab-7608fdac892d",
    "c90dc32e-01a6-474d-a10c-0278d5fae338",
    "1db0c01b-f718-4c18-92b4-077bca9c3616",
    "2655424f-21df-4f4c-a72a-ef7a3da2c98c",
    "6264dae6-05bd-4317-a519-9477d864e0f1",
    "4307b559-232a-43ef-83c1-92aeac45ef0c",
    "a60760de-a679-4ebe-9891-ce3a52cc6ece",
    "48501f00-b810-4ae6-9d7d-47d2fc4b30ed",
    "1b30b0c5-2113-4176-bf64-ae3c4b148a17",
]

