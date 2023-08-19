from services.bramhastra.helpers.post_fcl_freight_helper import SpotSearch
from configs.env import APP_ENV


def apply_spot_search_fcl_freight_rate_statistic(request):
    if APP_ENV == "production":
        spot_search = SpotSearch(request.params)
        spot_search.set_format_and_existing_rate_stats()
        spot_search.set_new_stats()
        return {"success": True}
