from services.fcl_freight_rate.models.fcl_freight_rate_properties import FclFreightRateProperties
from playhouse.shortcuts import model_to_dict

def get_fcl_freight_rate_properties(rate_id):
    rp = FclFreightRateProperties.select().where(FclFreightRateProperties.rate_id == str(rate_id))
    object = rp.first()
    return model_to_dict(object) if object else {}
    