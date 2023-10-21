from uuid import UUID


HAZ_CLASSES = [
    "gases-2.1",
    "gases-2.2",
    "gases-2.3",
    "flammable_liquids-3",
    "flammable_solids-4.1",
    "flammable_solids_self_heat-4.2",
    "emit_flammable_gases_with_water-4.3",
    "imo_classes-5.1",
    "toxic_substances-6.1",
    "infectious_substances-6.2",
    "radioactive_material-7",
    "corrosives-8",
    "miscellaneous_dangerous_goods-9",
]

SEARCH_START_DATE_OFFSET = 2

DEFAULT_EXPORT_DESTINATION_DETENTION = 7

DEFAULT_IMPORT_DESTINATION_DETENTION = 4

MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT = 100000

MAX_PAGE_LIMIT = 1000

CONFIRMED_INVENTORY = {
    "service_provider_ids": ["536abfe7-eab8-4a43-a4c3-6ff318ce01b5"],  # CogoXpress
    "tag": "confirmed_inventory",
}

PREDICTED_RATES_SERVICE_PROVIDER_IDS = ["6cc6b696-60f6-480b-bcbe-92cc8e642531"]

DEFAULT_PAYMENT_TERM = "prepaid"

DEFAULT_SERVICE_PROVIDER_ID = '5dc403b3-c1bd-4871-b8bd-35543aaadb36'

INTERNAL_BOOKING = {"service_provider_id": "5dc403b3-c1bd-4871-b8bd-35543aaadb36"}

FAK_COMMODITY = "general"

MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT = 100000

DEFAULT_SPECIFICITY_TYPE = "shipping_line"

POTENTIAL_CONTAINERS_BOOKING_COUNTS = {"sme": 5, "large": 15, "enterprise": 50}

POTENTIAL_CONVERSION_RATIO = 0.1

FREE_DAYS_TYPES = ["detention", "demurrage", "plugin"]

DEFAULT_MAX_WEIGHT_LIMIT = {"20": 18, "40": 30, "40HC": 32.5, "45HC": 32.68}

HAZ_CLASSES = [
    "gases-2.1",
    "gases-2.2",
    "gases-2.3",
    "flammable_liquids-3",
    "flammable_solids-4.1",
    "flammable_solids_self_heat-4.2",
    "emit_flammable_gases_with_water-4.3",
    "imo_classes-5.1",
    "toxic_substances-6.1",
    "infectious_substances-6.2",
    "radioactive_material-7",
    "corrosives-8",
    "miscellaneous_dangerous_goods-9",
]

STANDARD_COMMODITIES = [
    "general",
    "white_goods",
    "pta",
    "agro",
    "cotton_and_yarn",
    "fabric_and_textiles",
    "raw_cotton",
    "rice_bran",
    "sugar_rice",
]

REFER_COMMODITIES = [
    "chilled",
    "frozen",
    "pharma",
    "meat",
    "sea_food",
    "fruits_and_veg",
]

OPEN_TOP_COMMODITIES = ["in_gauge_cargo"]

OPEN_SIDE_COMMODITIES = []

FLAT_RACK_COMMODITIES = ['in_gauge_cargo']

ISO_TANK_COMMODITIES = ['non_haz_solids', 'non_haz_liquids', 'non_haz_gases']

ALL_COMMODITIES = list(set((STANDARD_COMMODITIES + REFER_COMMODITIES + OPEN_TOP_COMMODITIES + OPEN_SIDE_COMMODITIES + FLAT_RACK_COMMODITIES + ISO_TANK_COMMODITIES + HAZ_CLASSES)))

CONTAINER_SIZES = ['20', '40', '40HC', '45HC']

CONTAINER_TYPES = ['standard', 'refer', 'open_top', 'open_side', 'flat_rack', 'iso_tank']

PROD_DATA_OPERATIONS_ASSOCIATE_ROLE_ID = ['dcdcb3d8-4dca-42c2-ba87-1a54bc4ad7fb']

TRADE_TYPES = ['import', 'export', 'domestic']

DEAFULT_RATE_PRODUCER_METHOD = 'latest'

COUNTRY_CODE_MAPPING = ["IN","VN"]

SEARCH_START_DATE_OFFSET = 2

MAX_VALUE = 1000000000000000

ALLOWED_RATE_PRODUCER_METHODS = ["minimum", "maximum", "latest"]

DEAFULT_RATE_PRODUCER_METHOD = "latest"



COUNTRY_CODES_MAPPING = {"india": "IN", "usa": "US", "europe":"", "china":"CN", "vietnam":"VN", "singapore":"SG"}

DEFAULT_PROCURED_BY_ID = "d862bb07-02fb-4adc-ae20-d6e0bda7b9c1"

RATE_FEEDBACK_RELEVANT_ROLE_ID = {
    'supplier_relations_manager' : UUID('568c5939-3721-4444-a0ff-4c0298bc948d'),
    'supply_owner_vietnam' : UUID('e0aa356c-2e4c-4cfd-b279-a6d3cdfa4edb'),
    'coe_head_vietnam' : UUID('0e68d129-6f07-4324-95ee-88731b35c0c4')
}

PROD_DATA_OPERATIONS_ASSOCIATE_ROLE_ID = ['dcdcb3d8-4dca-42c2-ba87-1a54bc4ad7fb']

ISO_TANK_COMMODITIES = ["non_haz_solids", "non_haz_liquids", "non_haz_gases"]

CONTAINER_SIZES = ["20", "40", "40HC", "45HC"]

CONTAINER_TYPES = [
     "standard",
     "refer",
     "open_top",
     "open_side",
     "flat_rack",
     "iso_tank",
 ]

ALL_COMMODITIES = list(
     set(
         (
             STANDARD_COMMODITIES
             + REFER_COMMODITIES
             + OPEN_TOP_COMMODITIES
             + OPEN_SIDE_COMMODITIES
             + FLAT_RACK_COMMODITIES
             + ISO_TANK_COMMODITIES
             + HAZ_CLASSES
         )
     )
 )

CHINA_COUNTRY_ID = '1b94734e-7d51-4e94-9dd2-ef96aee64a8f'

INDIA_COUNTRY_ID = '541d1232-58ce-4d64-83d6-556a42209eb7'

DEFAULT_RATE_TYPE = 'market_place'

RATE_ENTITY_MAPPING = {
  "6fd98605-9d5d-479d-9fac-cf905d292b88": ['6fd98605-9d5d-479d-9fac-cf905d292b88', 'b67d40b1-616c-4471-b77b-de52b4c9f2ff'],
  "b67d40b1-616c-4471-b77b-de52b4c9f2ff": ['b67d40b1-616c-4471-b77b-de52b4c9f2ff', '6fd98605-9d5d-479d-9fac-cf905d292b88'],
  "default": ['b67d40b1-616c-4471-b77b-de52b4c9f2ff', '6fd98605-9d5d-479d-9fac-cf905d292b88']
}

SERVICE_PROVIDER_FF='36cee6fb-eeaf-4643-9db5-397544339635'

VALUE_PROPS_TAG_MAPPING = {
    'confirmed_space_and_inventory': 'Confirmed space & inventory',
    'standard_local_charges': 'Standard Local Charges',
    'competitive_price': 'Competitive Price',
    'fixed_exchange_rate': 'Fixed Exchange Rate',
    'priority_booking': 'Priority Booking'
  }



CONFIRMED_INVENTORY = {
    'service_provider_ids': ["536abfe7-eab8-4a43-a4c3-6ff318ce01b5"], #CogoXpress
    'tag': "confirmed_inventory"
}

POSSIBLE_SOURCES_IN_JOB_MAPPINGS = ['expiring_rates','critical_ports', 'cancelled_shipments', 'spot_search', 'rate_request', 'rate_feedback']

REFRESH_TIME = 10800

