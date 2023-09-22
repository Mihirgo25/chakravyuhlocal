from services.bramhastra.helpers.shipment_fcl_freight_rate_statistic_helper import (
    Shipment,
)
from configs.env import APP_ENV
from services.bramhastra.enums import AppEnv, ShipmentAction


def apply_shipment_fcl_freight_rate_statistic(request):
    if APP_ENV == AppEnv.production.value:
        shipment = Shipment(request)
        if request.action == ShipmentAction.create.value:
            shipment.set()
        else:
            shipment.update()
    return {"succuss": True}
