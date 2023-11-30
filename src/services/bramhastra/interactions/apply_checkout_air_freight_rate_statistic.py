from services.bramhastra.helpers.checkout_air_freight_rate_statistic_helper import (
    Checkout,
)
from services.bramhastra.enums import CheckoutAction
from services.bramhastra.enums import AppEnv
from configs.env import APP_ENV


def apply_checkout_air_freight_rate_statistic(request):
    if APP_ENV == AppEnv.production.value:
        checkout = Checkout()
        if request.action == CheckoutAction.create.value:
            checkout.set(request.params)
    return {"success": True}