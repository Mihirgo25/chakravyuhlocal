from services.bramhastra.helpers.quotation_fcl_freight_rate_statistic_helper import Quotations
from configs.env import APP_ENV
from services.bramhastra.enums import AppEnv

def apply_quotation_fcl_freight_rate_statistic(request):
    if APP_ENV == AppEnv.production.value:
        quotation = Quotations(request.params)
        quotation.set()
