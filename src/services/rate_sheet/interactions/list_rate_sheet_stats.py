from src.services.rate_sheet.models.rate_sheet import RateSheet
from src.services.rate_sheet.models.rate_sheet_audits import RateSheetAudits


def list_rate_sheet_stats(filters, service_provider_id):
    stats_filters = {
        "uploaded": {"status": "uploaded"},
        "converted": {"status": "converted"},
        "complete": {"status": "complete"},
    }

    executors = ['uploaded', 'converted', 'complete']
    for key in executors:
        
    return
