from services.bramhastra.helpers.checkout_fcl_freight_rate_statistic_helper import Checkout
from services.bramhastra.enums import CheckoutAction


def apply_checkout_fcl_freight_rate_statistic(request):
    checkout = Checkout(request.params)
    if request.action == CheckoutAction.create.value:
        checkout.set_format_and_existing_rate_stats()
        checkout.set_new_stats()
    else:
        checkout.set_existing_stats()
    return {"success": True}
