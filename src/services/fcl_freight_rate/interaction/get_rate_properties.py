from services.fcl_freight_rate.models.fcl_freight_rate_properties import RateProperties
from playhouse.shortcuts import model_to_dict
from fastapi import HTTPException

def get_rate_props(rate_id):
    rp = RateProperties.select().where(RateProperties.rate_id == rate_id)
    object = rp.first()
    return model_to_dict(object)
    