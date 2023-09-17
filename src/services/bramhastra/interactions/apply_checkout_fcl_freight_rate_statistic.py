from services.bramhastra.helpers.checkout_fcl_freight_rate_statistic_helper import (
    Checkout,
)
from services.bramhastra.enums import CheckoutAction
from services.bramhastra.enums import AppEnv
from configs.env import APP_ENV


def apply_checkout_fcl_freight_rate_statistic(request):
    if APP_ENV == AppEnv.production.value:
        checkout = Checkout(request.params)
        if request.action == CheckoutAction.create.value:
            checkout.set()
            checkout.create()
    return {"success": True}
