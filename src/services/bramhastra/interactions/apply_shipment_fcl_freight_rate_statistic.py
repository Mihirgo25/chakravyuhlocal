from services.bramhastra.helpers.shipment_fcl_freight_rate_statistic_helper import (
    Shipment,
)
from configs.env import APP_ENV
from services.bramhastra.enums import AppEnv


def apply_shipment_fcl_freight_rate_statistic(request):
    if APP_ENV == AppEnv.production.value:
        shipment = Shipment(request)
        shipment.set()
    return {"succuss": True}
