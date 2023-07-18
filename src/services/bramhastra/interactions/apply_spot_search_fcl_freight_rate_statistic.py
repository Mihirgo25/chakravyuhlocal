from services.bramhastra.helpers.fcl_freight import SpotSearch


def apply_spot_search_fcl_freight_rate_statistic(request):
    spot_search = SpotSearch(request.params)
    spot_search.set_format_and_existing_rate_stats()
    spot_search.set_new_stats()
    return {"success": True}