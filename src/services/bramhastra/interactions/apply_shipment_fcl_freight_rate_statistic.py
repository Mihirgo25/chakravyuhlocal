from services.bramhastra.helpers.post_fcl_freight_helper import Shipment

def apply_shipment_fcl_freight_rate_statistic(request):
    shipment = Shipment(request)
    if request.update_params:
        return
    shipment.format()
