from services.bramhastra.helpers.post_fcl_freight_helper import Checkout

def apply_checkout_fcl_freight_rate_statistic(request):
    checkout = Checkout(request.params)
    checkout.set_format_and_existing_rate_stats()
    checkout.set_new_stats()
    return {"success": True}