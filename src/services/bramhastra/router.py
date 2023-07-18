from fastapi import APIRouter, Depends
from services.bramhastra.interactions.apply_spot_search_fcl_freight_rate_statistic import apply_spot_search_fcl_freight_rate_statistic
from services.bramhastra.request_params import ApplySpotSearchFclFreightRateStatistic
from  rms_utils.auth import authorize_token

bramhastra = APIRouter()

@bramhastra.get('/get_rate_life_cycle')
def get_rate_life_cycle():
    return 

@bramhastra.post('/apply_spot_search_fcl_freight_rate_statistic')
def apply_spot_search_fcl_freight_rate_statistic_func(request: ApplySpotSearchFclFreightRateStatistic):
    return apply_spot_search_fcl_freight_rate_statistic(request)

