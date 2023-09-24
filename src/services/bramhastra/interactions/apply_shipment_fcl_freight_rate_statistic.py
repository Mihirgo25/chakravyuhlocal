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
        elif request.shipment_update_params is not None:
            shipment.update()
        elif request.shipment_service_update_params is not None:
            shipment.update_service()
    return {"succuss": True}
