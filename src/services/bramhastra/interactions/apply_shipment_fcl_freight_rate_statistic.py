from services.bramhastra.helpers.post_fcl_freight_helper import Shipment
from services.bramhastra.enums import ShipmentAction


def apply_shipment_fcl_freight_rate_statistic(request):
    shipment = Shipment(request)
    if request.action == ShipmentAction.create.value:
        pass
    elif request.action == ShipmentAction.update.value:
        pass
