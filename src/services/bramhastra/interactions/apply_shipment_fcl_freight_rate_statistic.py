from services.bramhastra.helpers.shipment_fcl_freight_rate_statistic_helper import Shipment
from configs.env import APP_ENV


def apply_shipment_fcl_freight_rate_statistic(request):
    if APP_ENV == "production":
        shipment = Shipment(request)
        if request.force_update_params:
            return
        shipment.format()
