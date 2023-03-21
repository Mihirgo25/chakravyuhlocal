from src.services.rate_sheet.models.rate_sheet import RateSheet
from src.services.rate_sheet.models.rate_sheet_audits import RateSheetAudit
from src.services.rate_sheet.interactions.list_rate_sheets import list_rate_sheets
import concurrent.futures
from typing import Dict

def list_rate_sheet_stats(filters, service_provider_id):
    stats_filters = {
        "uploaded": {"status": "uploaded"},
        "converted": {"status": "converted"},
        "complete": {"status": "complete"},
    }

    executors = ['uploaded', 'converted', 'complete']
    # for key in executors:
    # figureout
    # count = ListRateSheets.run!(filters={"service_provider_id": service_provider_id, "status": key})["total_count"]
    # return {key: count}
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(list_rate_sheets, key, service_provider_id): key for key in ['uploaded', 'converted', 'complete']}
        results = {}
        for future in concurrent.futures.as_completed(futures):
            key = futures[future]
            try:
                result = future.result()
            except Exception as e:
                print(f"{key} raised an exception: {e}")
            else:
                results.update(result)

    print(results)
    return results

