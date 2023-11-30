from services.bramhastra.helpers.air_freight_rate_request_statistic_helper import (
    Request,
)
from services.bramhastra.enums import RequestAction
from configs.env import APP_ENV
from services.bramhastra.enums import AppEnv
from services.bramhastra.models.air_freight_rate_request_statistics import (
    AirFreightRateRequestStatistic,
)


def apply_air_freight_rate_request_statistic(request):
    if APP_ENV == AppEnv.production.value:
        with AirFreightRateRequestStatistic._meta.database.atomic():
            feedback = Request(params=request.params)
            if request.action == RequestAction.create.value:
                feedback.create()
            elif request.action == RequestAction.delete.value:
                feedback.update_statistics()
            feedback.update_air_freight_action(request.action)