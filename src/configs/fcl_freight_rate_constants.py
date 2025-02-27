from configs.global_constants import *

REQUEST_SOURCES = ['spot_search','shipment']
LOCATION_HIERARCHY = {
'port' : 1,
'country' : 2,
'trade' : 3,
'continent' : 4
}

LOCATION_PAIR_HIERARCHY = {
  'port:port' : 1,
  'port:country' : 2,
  'port:trade' : 3,
  'port:continent' : 4,
  'country:port' : 5,
  'country:country' : 6,
  'country:trade' : 7,
  'country:continent' : 8,
  'trade:port' : 9,
  'trade:country' : 10,
  'trade:trade' : 11,
  'trade:continent' : 12,
  'continent:port' : 13,
  'continent:country' : 14,
  'continent:trade' : 15,
  'continent:continent' : 16,
}

COMMODITY_SURCHARGE_CONTAINER_COMMODITY_MAPPINGS = {
  'standard' : STANDARD_COMMODITIES + HAZ_CLASSES,
  'refer' : REFER_COMMODITIES,
  'open_top' : OPEN_TOP_COMMODITIES,
  'open_side' : OPEN_SIDE_COMMODITIES,
  'flat_rack' : FLAT_RACK_COMMODITIES,
  'iso_tank' : ISO_TANK_COMMODITIES + HAZ_CLASSES
}

LOCAL_CONTAINER_COMMODITY_MAPPINGS = {
  'standard' : [None] + HAZ_CLASSES,
  'refer' : [None],
  'open_top' : [None],
  'open_side' : [None],
  'flat_rack' : [None],
  'iso_tank' : [None] + HAZ_CLASSES
}

FREIGHT_CONTAINER_COMMODITY_MAPPINGS = {
  'standard' : [FAK_COMMODITY] + STANDARD_COMMODITIES + HAZ_CLASSES,
  'refer' : REFER_COMMODITIES,
  'open_top' : OPEN_TOP_COMMODITIES,
  'open_side' : [FAK_COMMODITY] + OPEN_SIDE_COMMODITIES,
  'flat_rack' : FLAT_RACK_COMMODITIES,
  'iso_tank' : ISO_TANK_COMMODITIES + HAZ_CLASSES
}

DEFAULT_EXPORT_DESTINATION_DETENTION = 7

DEFAULT_IMPORT_DESTINATION_DETENTION = 4

DEFAULT_EXPORT_DESTINATION_DEMURRAGE = 0

DEFAULT_IMPORT_DESTINATION_DEMURRAGE = 0

DEFAULT_WEIGHT_FREE_LIMIT = {
  "20" : 18,
  "others" : 20
}

DEFAULT_FREE_DAY_LIMIT = 3

DEFAULT_LOCAL_AGENT_ID = "5dc403b3-c1bd-4871-b8bd-35543aaadb36" #cogo freight

DEFAULT_SOURCED_BY_ID = '7f6f97fd-c17b-4760-a09f-d70b6ad963e8' # rishi agarwal

DEFAULT_PROCURED_BY_ID = '4c84b487-4964-40e9-8d8f-035f5c0f4b25' # cogo freight

DEFAULT_DASHBOARD_FCL_FREIGHT_SERVICE_PROVIDER = '5dc403b3-c1bd-4871-b8bd-35543aaadb36'

DEFAULT_SERVICE_PROVIDER_ID = '5dc403b3-c1bd-4871-b8bd-35543aaadb36'

SOURCES = ['tech_ops_dashboard', 'purchase_invoice', 'rms_upload', 'cogo_lens', 'rate_extension', 'rate_sheet', 'flash_booking', 'spot_negotiation', 'shipment', 'missing_rate', 'disliked_rate']

SCHEDULE_TYPES = ['direct', 'transhipment']

DEFAULT_SCHEDULE_TYPES = 'direct'

POSSIBLE_FEEDBACKS = ['unsatisfactory_rate', 'unsatisfactory_destination_detention', 'unpreferred_shipping_lines']

FEEDBACK_SOURCES = ['spot_search', 'checkout']

FEEDBACK_TYPES = ['liked', 'disliked']

DEFAULT_WEIGHT_LIMITS_FOR_PREDICTION = {
  '20' : {
    'free_limit': 18.0,
    'slabs': [
      {
        'lower_limit': 19,
        'upper_limit': 1000,
        'price': 0,
        'currency': 'USD'
      }
    ]
  },
  '40' : {
    'free_limit': 26.0,
    'slabs': [
      {
        'lower_limit': 27,
        'upper_limit': 1000,
        'price': 0,
        'currency': 'USD'
      }
    ]
  },
  '40HC' : {
    'free_limit': 26.0,
    'slabs': [
      {
        'lower_limit': 27,
        'upper_limit': 1000,
        'price': 0,
        'currency': 'USD'
      }
    ]
  },
  '45HC' : {
    'free_limit': 26.0,
    'slabs': [
      {
        'lower_limit': 27,
        'upper_limit': 1000,
        'price': 0,
        'currency': 'USD'
      }
    ]
  }
}

OVERWEIGHT_SURCHARGE_LINE_ITEM = {
  'code': 'OWS',
  'unit': 'per_container',
  'name': 'Overweight Surcharge'
}

ROLE_IDS_FOR_NOTIFICATIONS = ['70710ab2-0f80-4e12-a4f5-d75660c05315', 'dcdcb3d8-4dca-42c2-ba87-1a54bc4ad7fb']  # Supply Agent/Prod_Data Operation Associete

LOCATION_HIERARCHY_FOR_WEIGHT = {
  '' : 0,
  'seaport' : 1,
  'country' : 2
}

CONTAINER_CLUSTERS = { '40_40HC' : ['40', '40HC'] }

PAYMENT_TERM = ['prepaid', 'collect']

DEFAULT_PAYMENT_TERM = 'prepaid'

SPECIFICITY_TYPE = ['cogoport', 'shipping_line', 'rate_specific']

DEFAULT_SPECIFICITY_TYPE = 'shipping_line'

TECHOPS_TASK_ABORT_REASONS = [
  'Sid Cancelled/Changed',
  'Port Currently not served',
  'Wrong/Invalid request'
]

RATE_ENTITY_MAPPING = {
  "6fd98605-9d5d-479d-9fac-cf905d292b88": ['6fd98605-9d5d-479d-9fac-cf905d292b88', 'b67d40b1-616c-4471-b77b-de52b4c9f2ff'],
  "b67d40b1-616c-4471-b77b-de52b4c9f2ff": ['b67d40b1-616c-4471-b77b-de52b4c9f2ff', '6fd98605-9d5d-479d-9fac-cf905d292b88'],
  "default": ['b67d40b1-616c-4471-b77b-de52b4c9f2ff', '6fd98605-9d5d-479d-9fac-cf905d292b88']
}

VALID_UNITS = ['per_bl', 'per_container', 'per_shipment']

EXPECTED_TAT = 6 # HOURS

EXPECTED_TAT_RATE_FEEDBACK_REVERT = 48 # HOURS

DEFAULT_LOCAL_AGENT_IDS = {
  "541d1232-58ce-4d64-83d6-556a42209eb7":{'platform_config_constant_id':'3617e7ea-fc4f-4478-aea2-651fcb0ec1e6', 'value_type':'default', 'value':'5dc403b3-c1bd-4871-b8bd-35543aaadb36', 'display_name':'COGO FREIGHT PRIVATE LIMITED', 'status':'active'},
  "default": {'platform_config_constant_id':'3617e7ea-fc4f-4478-aea2-651fcb0ec1e6', 'value_type':'default', 'value':'5dc403b3-c1bd-4871-b8bd-35543aaadb36', 'display_name':'COGO FREIGHT PRIVATE LIMITED', 'status':'active'}
}


TOP_SHIPPING_LINES_FOR_PREDICTION = [
  'c3649537-0c4b-4614-b313-98540cffcf40', #'Maersk'
  'a2a447b4-0ce5-4d3c-afa9-2f81b313aecd', #'MSC'
  'fb1aa2f1-d136-4f26-ad8f-2e1545cc772a', #'Hapag Lloyd'
  '2d477bb2-8956-4dbe-bd8b-71144b60374c', #'ONE Line'
  'b2f92d49-6180-43bd-93a5-4d64f5819a9b', #'CMA CGM'
  '256c0d0c-e0f1-439b-8c3b-70edfe27278e', #'Evergreen'
  '3c5d996c-4d4e-4a2b-bce7-1024b46f7300', #'Cosco'
  '83af97eb-09a7-4a17-a3ca-561f0bbc0b6f', #'Emirates'
  '3b786382-f751-43b0-a0a6-2ff1a6128be4', #'Hyundai'
  '9ee49704-f5a7-4f17-9e25-c5c3b5ec3d1d', #'OOCL'
  'bfd2a958-b70c-4f2e-ae9b-f66f5a211535', #'Wan Hai'
  'be57f277-0c81-47b4-9322-bf06ccc5314c', #'Zim'
  '2df9777e-01e9-4f86-83b8-28b36ddf1be1', #'PIL'
  '25c0df76-5e1a-4f14-9c85-e7f794d8e8b9'  #'ANL'
]

EXTENSION_ENABLED_MODES = ['manual', 'flash_booking', 'missing_rate', 'disliked_rate', 'spot_negotation', 'rate_sheet']

COGO_ASSURED_SHIPPING_LINE_ID = 'e6da6a42-cc37-4df2-880a-525d81251547' #cogo-line

DEFAULT_SHIPPING_LINE_ID = 'e6da6a42-cc37-4df2-880a-525d81251547' #cogo-line

DEFAULT_PROCURED_BY_ID = "2dbe768e-929d-4e54-baf0-309ef68c978b" #cogo-envision

COGO_ASSURED_SERVICE_PROVIDER_ID = "5dc403b3-c1bd-4871-b8bd-35543aaadb36"

DEFAULT_SOURCED_BY_ID = "7f6f97fd-c17b-4760-a09f-d70b6ad963e8"

VALUE_PROPOSITIONS = ['confirmed_space_and_inventory', 'standard_local_charges', 'competitive_price', 'fixed_exchange_rate', 'priority_booking']

DEFAULT_VALUE_PROPS = [{"name": "confirmed_space_and_inventory", "free_limit": None}]

RATE_TYPES = ['market_place', 'cogo_assured', 'promotional', 'spot_booking']

DEFAULT_RATE_TYPE = 'market_place'

DEFAULT_PERFORMED_BY_TYPE = 'system'

VN_ENTITY_ID = 'b67d40b1-616c-4471-b77b-de52b4c9f2ff'

SPECIFICITY_TYPE_HIERARCHY = {
    'rate_specific':1,
    'shipping_line':2,
    'cogoport':3
}


REQUIRED_FEEDBACK_STATS_REQUEST_KEYS = {'likes_count','dislikes_count'}

FCL_IMPORT_COVERAGE_USERS = [
  'f47788fe-85e8-4f86-a9d7-7c7902ea864a',
  '51641e0e-a5da-452a-81fc-ccb8fe6df343',
  '922b367f-0f3e-4872-91d0-68413fc7f955'
]

FCL_EXPORT_COVERAGE_USERS = [
  '6addea60-a3de-4067-b08d-ece04be594ab',
  'd7f62f2d-2b41-41ae-a9f0-200255de4d8f',
  '329fb317-f2f9-4c41-aabd-4a9befc53721'
]

CRITICAL_PORTS_INDIA_VIETNAM = [
    'eb187b38-51b2-4a5e-9f3c-978033ca1ddf',
    '7aa6ac82-c295-497f-bfe1-90294cdfa7a9',
    '3c843f50-867c-4b07-bb57-e61af97dabfe',
    'b0a48e84-48d5-438b-841a-e800fb68e439',
    'c2d6fb91-2875-4d73-b12b-dd1b78fdfe8a',
    '76fdeee3-1c7f-4f6e-a5d2-2a729445f2d9'
]

MIN_ALLOWED_PERCENTAGE_CHANGE = -3
MAX_ALLOWED_PERCENTAGE_CHANGE = 15
MIN_ALLOWED_MARKUP = -50
MAX_ALLOWED_MARKUP = 100

REQUIRED_FEEDBACK_STATS_REQUEST_KEYS = {'likes_count','dislikes_count'}

FCL_FREIGHT_FALLBACK_FAKE_SCHEDULES = [
    {
        'departure_offset_days': 7,
        'transit_time': 11,
        'number_of_stops': 0,
        'schedule_type': DEFAULT_SCHEDULE_TYPES
    }
]