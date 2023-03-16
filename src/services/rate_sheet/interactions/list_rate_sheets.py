

from typing import List, Dict
from src.services.rate_sheet.models.rate_sheet import RateSheet
from src.services.rate_sheet.models.rate_sheet_audits import RateSheetAudits
from libs.get_filters import get_filters
import services.rate_sheet.interactions.new_list_rate_sheets as list_rate_sheet

POSSIBLE_DIRECT_FILTERS = ['id', 'agent_id', 'service_provider_id', 'status', 'service_name', 'serial_id', 'cogo_entity_id']
POSSIBLE_INDIRECT_FILTERS = ['performed_by_id', 'partner_id']

def get_query():
    return

def apply_direct_filters(query, filters):
    direct_filters = [(k, v) for k, v in filters.items() if k in POSSIBLE_DIRECT_FILTERS]
    query = get_filters(direct_filters, query, RateSheet, "")
    return query

def apply_indirect_filters(query, filters, fields):
    for key, val in filters.items():
        query = getattr(list_rate_sheet, "apply_{}_filter".format(key))(
            query, val, fields, filters
        )
    return query

def apply_partner_id_filter(query, val, fields, filters):
    cogo_entity_id = filters['partner_id']
    query = query.where(RateSheet.cogo_entity_id == cogo_entity_id)
    return query

def apply_performed_by_id_filter(query, val, fields, filters):
    return query


def list_rate_sheets(filters, sort_by, sort_type, page_limit, page, pagination_data_required):
    query = RateSheet.select()
    query = apply_direct_filters(query, filters)
    query = apply_direct_filters(query, filters)


