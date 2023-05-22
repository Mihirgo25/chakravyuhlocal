from services.fcl_freight_rate.models.fcl_freight_rate_properties import RateProperties
from playhouse.shortcuts import model_to_dict

def get_fcl_freight_rate_properties(rate_id):
    rp = RateProperties.select(RateProperties.id).where(RateProperties.rate_id == rate_id)
    object = rp.first()
    return model_to_dict(object) if object else {}
    