from src.services.rate_sheet.models.rate_sheet import RateSheet
from src.services.rate_sheet.models.rate_sheet_audits import RateSheetAudits

POSSIBLE_DIRECT_FILTERS = ['id', 'agent_id', 'service_provider_id', 'status', 'service_name', 'serial_id', 'cogo_entity_id']
POSSIBLE_INDIRECT_FILTERS = ['performed_by_id', 'partner_id']

# RateSheet
# RateSheetAudit
# organization
# user

def get_query(query, sort_by, sort_type, page, page_limit):
    query = RateSheet.order(f"#{sort_by} #{sort_type}").page(page).per(page_limit)
    return query


def list_rate_sheets(filters, sort_by, sort_type, page_limit, page, pagination_data_required):
    query = get_query(query, sort_by, sort_type, page, page_limit)
    return
