from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from datetime import datetime

def get_expired_fcl_freight_rates():
    data = list(FclFreightRate.select(FclFreightRate.id).where(FclFreightRate.last_rate_available_date <= datetime.now()).limit(1).dicts())
    return data