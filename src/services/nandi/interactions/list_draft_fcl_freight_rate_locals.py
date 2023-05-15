from services.nandi.models.draft_fcl_freight_rate_local import DraftFclFreightRateLocal
from libs.get_filters import get_filters
from libs.get_applicable_filters import get_applicable_filters
import json
from fastapi.encoders import jsonable_encoder

possible_direct_filters = ["id", "commodity", "container_size", "container_type", "port_id", "shipping_line_id", "trade_type", "rate_id", "source", "status", "shipment_serial_id"]
possible_indirect_filters = []

def list_draft_fcl_freight_rate_locals(filters = {}, page_limit = 10, page = 1, sort_by = 'updated_at', sort_type = 'desc', return_query = False):
    query = get_query(sort_by, sort_type)

    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)

            direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)

            query = get_filters(direct_filters, query, DraftFclFreightRateLocal)

            if return_query:
                return {'list': query} 

            data = get_data(query)
            return { 'list': data }

def get_query(sort_by, sort_type):
    query = DraftFclFreightRateLocal.select().order_by(eval("DraftFclFreightRateLocal.{}.{}()".format(sort_by, sort_type)))
    return query

def get_data(query):
    data = jsonable_encoder(list(query.dicts()))
    return data