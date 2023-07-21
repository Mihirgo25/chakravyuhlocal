from fastapi import APIRouter, Depends, Query
from services.bramhastra.interactions.apply_spot_search_fcl_freight_rate_statistic import (
    apply_spot_search_fcl_freight_rate_statistic,
)
from services.bramhastra.interactions.apply_checkout_fcl_freight_rate_statistic import (
    apply_checkout_fcl_freight_rate_statistic,
)
from services.bramhastra.interactions.get_fcl_freight_rate_charts import (
    get_fcl_freight_rate_stats,
)
from services.bramhastra.request_params import (
    ApplySpotSearchFclFreightRateStatistic,
    ApplyCheckoutFclFreightRateStatistic,
)
from rms_utils.auth import authorize_token
from pydantic.types import Json
from typing import Annotated
from datetime import date
from services.bramhastra.response_models import FclFreightRateCharts
from fastapi.responses import JSONResponse
import time

bramhastra = APIRouter()

@bramhastra.post("/apply_spot_search_fcl_freight_rate_statistic")
def apply_spot_search_fcl_freight_rate_statistic_func(
    request: ApplySpotSearchFclFreightRateStatistic,
):
    return apply_spot_search_fcl_freight_rate_statistic(request)


@bramhastra.post("/apply_checkout_fcl_freight_rate_statistic")
def apply_checkout_fcl_freight_rate_statistic_func(
    request: ApplyCheckoutFclFreightRateStatistic,
):
    return apply_checkout_fcl_freight_rate_statistic(request)


@bramhastra.get("/get_fcl_freight_rate_charts")
async def get_fcl_freight_rate_charts_func(
    filters: Annotated[Json, Query()] = None,
) -> FclFreightRateCharts:
    start = time.time()
    response =  await get_fcl_freight_rate_stats(filters)
    print(time.time()-start)
    return JSONResponse(content=response)
