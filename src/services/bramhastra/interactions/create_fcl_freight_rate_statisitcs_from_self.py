from services.bramhastra.fcl_freight import Rate

def create_fcl_freight_rate_statistics_from_self(params):
    Rate.apply_create_stats()