from services.bramhastra.helpers.spot_search_air_freight_statistic_helper import (
    SpotSearch,
)
from configs.env import APP_ENV
from services.bramhastra.enums import AppEnv
from services.bramhastra.enums import AppEnv
from services.bramhastra.models.air_freight_rate_statistic import (
    AirFreightRateStatistic,
)


def apply_spot_search_air_freight_rate_statistic(request):
    if APP_ENV == AppEnv.production.value:
        with AirFreightRateStatistic._meta.database.atomic():
            spot_search = SpotSearch()
            spot_search.set(request.params)
            return {"success": True}
