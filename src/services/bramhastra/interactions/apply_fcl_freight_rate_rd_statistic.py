from services.bramhastra.helpers.post_fcl_freight_helper import RevenueDesk

def apply_fcl_freight_rate_rd_statistic(request):
    RevenueDesk(request).set_rate_stats()
        