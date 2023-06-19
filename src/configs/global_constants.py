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

FLAT_RACK_COMMODITIES = ["in_gauge_cargo"]

ISO_TANK_COMMODITIES = ["non_haz_solids", "non_haz_liquids", "non_haz_gases"]

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

CONTAINER_SIZES = ["20", "40", "40HC", "45HC"]

CONTAINER_TYPES = [
    "standard",
    "refer",
    "open_top",
    "open_side",
    "flat_rack",
    "iso_tank",
]

PROD_DATA_OPERATIONS_ASSOCIATE_ROLE_ID = ["dcdcb3d8-4dca-42c2-ba87-1a54bc4ad7fb"]

TRADE_TYPES = ["import", "export", "domestic"]

ALLOWED_RATE_PRODUCER_METHODS = ["minimum", "maximum", "latest"]

DEAFULT_RATE_PRODUCER_METHOD = "latest"



COUNTRY_CODES_MAPPING = {"india": "IN", "usa": "US", "europe":"", "china":"CN"}

DEFAULT_WEIGHT_SLABS=[
    {
        'lower_limit':0.0,
        'upper_limit':50,
        'tariff_price':0,
        'currency':'INR',
        'unit':'per_kg'
    },
    {
        'lower_limit':50.1,
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
    },{
        'lower_limit':1000.1,
        'upper_limit':10000,
        'currency':'INR',
        'tariff_price':0,
        'unit':'per_kg'
    }

]
DEFAULT_AIRLINE_ID = '853f3c4c-af7f-4912-98a8-1515000bcd20'

DEFAULT_PROCURED_BY_ID = "d862bb07-02fb-4adc-ae20-d6e0bda7b9c1"

RATE_FEEDBACK_RELEVANT_ROLE_ID = {
    'supplier_relations_manager' : UUID('568c5939-3721-4444-a0ff-4c0298bc948d'),
    'supply_owner_vietnam' : UUID('e0aa356c-2e4c-4cfd-b279-a6d3cdfa4edb'),
    'coe_head_vietnam' : UUID('0e68d129-6f07-4324-95ee-88731b35c0c4')
}
CHINA_COUNTRY_ID = '1b94734e-7d51-4e94-9dd2-ef96aee64a8f'

INDIA_COUNTRY_ID = '541d1232-58ce-4d64-83d6-556a42209eb7'
