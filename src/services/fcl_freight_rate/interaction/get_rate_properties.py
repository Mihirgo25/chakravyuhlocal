from services.fcl_freight_rate.models.fcl_freight_rate_properties import RateProperties
from fastapi import HTTPException

def get_rate_props(rate_id):
    rp = RateProperties.select().where(RateProperties.rate_id == rate_id).first()
    return rp