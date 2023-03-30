from services.rate_sheet.models.rate_sheet import RateSheet
from services.rate_sheet.models.rate_sheet_audits import RateSheetAudit
from services.rate_sheet.interactions.list_rate_sheets import list_rate_sheets
import concurrent.futures
from typing import Dict

def list_rate_sheet_stats(filter, service_provider_id):
    stats_filters = {
        "uploaded": {"status": "uploaded"},
        "converted": {"status": "converted"},
        "complete": {"status": "complete"},
    }
    stats = {}
    for key, val in stats_filters.items():
        filter = val
        filter['service_provider_id']= service_provider_id
        stats[key] = list_rate_sheets(filters= filter)['total_count']

    return stats


