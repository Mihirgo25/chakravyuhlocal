from services.bramhastra.helpers.quotation_fcl_freight_rate_statistic_helper import Quotations
from configs.env import APP_ENV


def apply_quotation_fcl_freight_rate_statistic(request):
    if APP_ENV == "production":
        quotation = Quotations(request.params)
        quotation.set()
