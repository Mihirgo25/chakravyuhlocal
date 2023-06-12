AIR_STANDARD_VOLUMETRIC_WEIGHT_CONVERSION_RATIO = 166.67
DEFAULT_SERVICE_PROVIDER_ID = '5dc403b3-c1bd-4871-b8bd-35543aaadb36'
DEFAULT_FACTOR = 0.89
from configs.global_constants import *

RATE_ENTITY_MAPPING = {
  "6fd98605-9d5d-479d-9fac-cf905d292b88": ['6fd98605-9d5d-479d-9fac-cf905d292b88', 'b67d40b1-616c-4471-b77b-de52b4c9f2ff'],
  "b67d40b1-616c-4471-b77b-de52b4c9f2ff": ['b67d40b1-616c-4471-b77b-de52b4c9f2ff', '6fd98605-9d5d-479d-9fac-cf905d292b88'],
  "default": ['b67d40b1-616c-4471-b77b-de52b4c9f2ff', '6fd98605-9d5d-479d-9fac-cf905d292b88']
}
MAX_CARGO_LIMIT=10000000.0
REQUEST_SOURCES = ['spot_search', 'shipment']

AIR_STANDARD_VOLUMETRIC_WEIGHT_CONVERSION_RATIO = 166.67

AIR_TRADE_IMPORT_TYPE='import'

AIR_TRADE_EXPORT_TYPE='export'

AIR_IMPORTS_HIGH_DENSITY_RATIO = 0.835

AIR_IMPORTS_LOW_DENSITY_RATIO = 1.10

AIR_EXPORTS_HIGH_DENSITY_RATIO = 0.6

AIR_EXPORTS_LOW_DENSITY_RATIO = 1.2

MAX_CARGO_LIMIT = 10000000.0

COMMODITY = ['general','special_consideration']

COMMODITY_TYPE=AIR_GENERAL_COMMODITY_TYPE+AIR_SPECIAL_CONSIDERATION_COMMODITY_TYPES

LOCAL_COMMODITIES = AIR_STANDARD_COMMODITIES + AIR_HAZARDOUS_COMMODITIES

TECHOPS_TASK_ABORT_REASONS = [
    'sid_cancelled/changed',
    'airport_currently_not_served'
  ]

DEFAULT_SERVICE_PROVIDER_ID = '536abfe7-eab8-4a43-a4c3-6ff318ce01b5'

DEFAULT_SOURCED_BY_ID = '7f6f97fd-c17b-4760-a09f-d70b6ad963e8'


FEEDBACK_TYPES = ['liked', 'disliked']

POSSIBLE_FEEDBACKS = ['unsatisfactory_rate', 'unsatisfactory_destination_storage', 'unpreferred_airlines']

FEEDBACK_SOURCES = ['spot_search', 'checkout']

REQUEST_SOURCES = ['spot_search', 'shipment']

FEEDBACK_SOURCES = ['spot_search', 'checkout','rate_sheet']

FEEDBACK_TYPES = ['liked', 'disliked']

PRICE_TYPES = ['net_net', 'all_in']

COMMODITY = ["general","special_consideration"]

PACKING_TYPE = ["pallet", "box", "crate", "loose"]
HANDLING_TYPE = ["stackable", "non_stackable"]

COMMODITY_SUB_TYPE = []

RATE_TYPES = ['market_place','promotional','consolidated','cogo_assured']

AIR_OPERATION_TYPES = ['passenger', 'freighter', 'charter', 'prime', 'lean']

EXPECTED_TAT = 2

ROLE_IDS_FOR_NOTIFICATIONS = ['70710ab2-0f80-4e12-a4f5-d75660c05315', 'dcdcb3d8-4dca-42c2-ba87-1a54bc4ad7fb']

DEFAULT_AIRLINE_IDS= ['e942211b-f46f-4a07-9756-626377218d1d','83af97eb-09a7-4a17-a3ca-561f0bbc0b6f','3a8dc0d2-2bb9-40f4-b9c4-993b6bf273e4']

COGOLENS_URL = 'https://lens.cogoport.com/cogolens/create_air_freight_rate_prediction'

SLAB_WISE_CHANGE_FACTOR = 0.89

COGO_ENVISION_ID = '2dbe768e-929d-4e54-baf0-309ef68c978b'