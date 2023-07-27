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
from services.bramhastra.interactions.get_fcl_freight_rate_lifecycle import (
    get_fcl_freight_rate_lifecycle,
)
from services.bramhastra.interactions.get_fcl_freight_map_view_statistics import (
    get_fcl_freight_map_view_statistics,
)
from services.bramhastra.interactions.get_fcl_freight_rate_world import (
    get_fcl_freight_rate_world,
)
from services.bramhastra.interactions.list_fcl_freight_rate_statistics import (
    list_fcl_freight_rate_statistics,
)
from services.bramhastra.request_params import (
    ApplySpotSearchFclFreightRateStatistic,
    ApplyCheckoutFclFreightRateStatistic,
)
from pydantic.types import Json
from typing import Annotated
from services.bramhastra.response_models import (
    FclFreightRateCharts,
    FclFreightRateDistribution,
    FclFreightRateLifeCycleResponse,
    DefaultList,
    FclFreightRateWorldResponse,
)
from fastapi.responses import JSONResponse
from services.bramhastra.constants import INDIA_LOCATION_ID

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


@bramhastra.get("/get_fcl_freight_rate_charts", response_model=FclFreightRateCharts)
def get_fcl_freight_rate_charts_func(
    filters: Annotated[Json, Query()] = {},
):
    response = get_fcl_freight_rate_charts(filters)
    return JSONResponse(content=response)


@bramhastra.get(
    "/get_fcl_freight_rate_distribution", response_model=FclFreightRateDistribution
)
def get_fcl_freight_rate_distribution_func(
    filters: Annotated[Json, Query()] = {},
):
    response = get_fcl_freight_rate_distribution(filters)
    return JSONResponse(content=response)


@bramhastra.get(
    "/get_fcl_freight_rate_lifecycle", response_model=FclFreightRateLifeCycleResponse
)
async def get_fcl_freight_rate_lifecycle_func(
    filters: Annotated[Json, Query()] = {},
):
    response = await get_fcl_freight_rate_lifecycle(filters)
    return JSONResponse(content=response)


@bramhastra.get("/get_fcl_freight_map_view_statistics", response_model=DefaultList)
def get_fcl_freight_map_view_statistics_func(
    filters: Annotated[Json, Query()] = {
        "origin": {"type": "country", "id": INDIA_LOCATION_ID}
    },
    page_limit: int = 30,
    page: int = 1,
):
    response = get_fcl_freight_map_view_statistics(filters, page_limit, page)
    return JSONResponse(content=response)


@bramhastra.get(
    "/get_fcl_freight_rate_world", response_model=FclFreightRateWorldResponse
)
def get_fcl_freight_rate_world_func():
    response = get_fcl_freight_rate_world()
    return JSONResponse(content=response)


@bramhastra.get("/list_fcl_freight_rate_statistics", response_model=DefaultList)
async def list_fcl_freight_rate_statistics_func(
    filters: Annotated[Json, Query()] = {},
    page_limit: int = 10,
    page: int = 1,
):
    response = await list_fcl_freight_rate_statistics(filters, page_limit, page)
    return JSONResponse(content=response)
