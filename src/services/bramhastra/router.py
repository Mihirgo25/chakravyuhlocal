from fastapi import APIRouter, Depends, Query
from services.bramhastra.interactions.apply_spot_search_fcl_freight_rate_statistic import (
    apply_spot_search_fcl_freight_rate_statistic,
)
from services.bramhastra.interactions.apply_checkout_fcl_freight_rate_statistic import (
    apply_checkout_fcl_freight_rate_statistic,
)
from services.bramhastra.interactions.get_fcl_freight_rate_charts import (
    get_fcl_freight_rate_charts,
)
from services.bramhastra.interactions.get_fcl_freight_rate_distribution import (
    get_fcl_freight_rate_distribution,
)
from services.bramhastra.interactions.get_fcl_freight_rate_drilldown import get_fcl_freight_rate_drilldown
from services.bramhastra.interactions.get_fcl_freight_map_view_statistics import get_fcl_freight_map_view_statistics
from services.bramhastra.request_params import (
    ApplySpotSearchFclFreightRateStatistic,
    ApplyCheckoutFclFreightRateStatistic,
)
from rms_utils.auth import authorize_token
from pydantic.types import Json
from typing import Annotated
from datetime import date
from services.bramhastra.response_models import (
    FclFreightRateCharts,
    FclFreightRateDistribution,
    FclFreightRateDrillDownResponse
)
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
    filters: Annotated[Json, Query()] = {},
) -> FclFreightRateCharts:
    start = time.time()
    response = await get_fcl_freight_rate_charts(filters)
    print(time.time() - start)
    return JSONResponse(content=response)


@bramhastra.get("/get_fcl_freight_rate_distribution")
def get_fcl_freight_rate_distribution_func(
    filters: Annotated[Json, Query()] = {},
) -> FclFreightRateDistribution:
    start = time.time()
    response = get_fcl_freight_rate_distribution(filters)
    print(time.time() - start)
    return JSONResponse(content=response)


@bramhastra.get("/get_fcl_freight_rate_drilldown")
def get_fcl_freight_rate_drilldown_func(
    filters: Annotated[Json, Query()] = {},
) -> FclFreightRateDrillDownResponse:
    start = time.time()
    response = get_fcl_freight_rate_drilldown(filters)
    print(time.time() - start)
    return JSONResponse(content=response)


@bramhastra.get("/get_fcl_freight_map_view")
def get_fcl_freight_map_view_statistics_func(
    filters: Annotated[Json, Query()] = {},
):
    start = time.time()
    response = get_fcl_freight_map_view_statistics(filters)
    print(time.time() - start)
    return JSONResponse(content=response)
