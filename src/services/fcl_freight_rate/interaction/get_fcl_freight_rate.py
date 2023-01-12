from services.fcl_freight_rate.models.fcl_freight_rates import FclFreightRate
from datetime import datetime
import json

def get_fcl_freight_rate():
    data = list(FclFreightRate.select(FclFreightRate.validities).where(FclFreightRate.last_rate_available_date >= datetime.now()).limit(10).dicts())
    return data