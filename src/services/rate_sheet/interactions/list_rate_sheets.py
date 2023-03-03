from typing import List, Dict
from src.services.rate_sheet.models.rate_sheet import RateSheet
from src.services.rate_sheet.models.rate_sheet_audits import RateSheetAudits

POSSIBLE_DIRECT_FILTERS = ['id', 'agent_id', 'service_provider_id', 'status', 'service_name', 'serial_id', 'cogo_entity_id']
POSSIBLE_INDIRECT_FILTERS = ['performed_by_id', 'partner_id']

def get_query(filters: Dict, sort_by: str, sort_type: str, page: int, page_limit: int) -> RateSheet:
    query = RateSheet.query

    for filter_name, filter_value in filters.items():
        if filter_name in POSSIBLE_DIRECT_FILTERS:
            query = query.filter(getattr(RateSheet, filter_name) == filter_value)
        elif filter_name in POSSIBLE_INDIRECT_FILTERS:
            query = query.join(RateSheetAudits).filter(getattr(RateSheetAudits, filter_name) == filter_value)

    query = query.order_by(getattr(RateSheet, sort_by).asc() if sort_type == 'asc' else getattr(RateSheet, sort_by).desc())
    query = query.paginate(page=page, per_page=page_limit)
    return query

def list_rate_sheets(filters: Dict, sort_by: str, sort_type: str, page_limit: int, page: int, pagination_data_required: bool) -> Dict:
    query = get_query(filters, sort_by, sort_type, page, page_limit)
    rate_sheets = query.items

    if pagination_data_required:
        return {
            "rate_sheets": [rate_sheet.to_dict() for rate_sheet in rate_sheets],
            "total_pages": query.pages,
            "total_rate_sheets": query.total
        }
    else:
        return {"rate_sheets": [rate_sheet.to_dict() for rate_sheet in rate_sheets]}
