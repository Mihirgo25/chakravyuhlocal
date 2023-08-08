from services.bramhastra.helpers.post_fcl_freight_helper import Quotations

def apply_quotation_fcl_freight_rate_statistic(request):
    quotation = Quotations(request)
    quotation.execute()