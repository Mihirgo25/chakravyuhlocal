from services.bramhastra.helpers.spot_search_fcl_freight_statistic_helper import (
    SpotSearch,
)
from configs.env import APP_ENV
from services.bramhastra.enums import AppEnv
from services.bramhastra.enums import AppEnv
from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)


def apply_spot_search_fcl_freight_rate_statistic(request):
    if APP_ENV == AppEnv.production.value:
        with FclFreightRateStatistic._meta.database.atomic():
            spot_search = SpotSearch(request.params)
            spot_search.set()
            spot_search.create()
            return {"success": True}
