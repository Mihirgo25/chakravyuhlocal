from services.supply_tool.models.fcl_freight_rate_jobs import FclFreightRateJobs
import json
from libs.get_applicable_filters import get_applicable_filters
from libs.get_filters import get_filters
from libs.json_encoder import json_encoder

possible_direct_filters = ['origin_port_id','destination_port_id','shipping_line_id','commodity','status']
possible_indirect_filters = ['updated_at', 'user_id', 'date_range']

def list_fcl_freight_rate_stats(filters = {}, page_limit = 10, page = 1, sort_by = 'updated_at', sort_type = 'desc'):

    return
    