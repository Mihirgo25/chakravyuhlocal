from fastapi import APIRouter, Depends, Query
from services.bramhastra.interactions.apply_spot_search_fcl_freight_rate_statistic import (
    apply_spot_search_fcl_freight_rate_statistic,
)
from services.bramhastra.interactions.apply_checkout_fcl_freight_rate_statistic import (
    apply_checkout_fcl_freight_rate_statistic,
)
from services.bramhastra.interactions.apply_shipment_fcl_freight_rate_statistic import (
    apply_shipment_fcl_freight_rate_statistic,
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
from services.bramhastra.interactions.list_fcl_freight_rate_request_statistics import (
    list_fcl_freight_rate_request_statistics,
)
from services.bramhastra.interactions.apply_fcl_freight_rate_rd_statistic import (
    apply_fcl_freight_rate_rd_statistic,
)
from services.bramhastra.interactions.apply_quotation_fcl_freight_rate_statistic import (
    apply_quotation_fcl_freight_rate_statistic,
)
from services.bramhastra.interactions.get_fcl_freight_port_pair_count import (
    get_fcl_freight_port_pair_count,
)
from services.bramhastra.interactions.get_fcl_freight_rate_deviation import get_fcl_freight_deviation

from services.bramhastra.request_params import (
    ApplySpotSearchFclFreightRateStatistic,
    ApplyCheckoutFclFreightRateStatistic,
    ApplyShipmentFclFreightRateStatistics,
    ApplyRevenueDeskFclFreightStatistics,
    ApplyQuotationFclFreightRateStatistics,
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
from services.bramhastra.constants import INDIAN_LOCATION_ID
from rms_utils.auth import authorize_token
from fastapi import HTTPException
import sentry_sdk

bramhastra = APIRouter()


@bramhastra.post("/apply_spot_search_fcl_freight_rate_statistic")
def apply_spot_search_fcl_freight_rate_statistic_api(
    request: ApplySpotSearchFclFreightRateStatistic,
    auth_response: dict = Depends(authorize_token),
):
    if auth_response.get("status_code") != 200:
        return JSONResponse(
            status_code=auth_response.get("status_code"), content=auth_response
        )

    try:
        apply_spot_search_fcl_freight_rate_statistic(request)
        return JSONResponse(status_code=200, content={"success": True})
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@bramhastra.post("/apply_quotation_fcl_freight_rate_statistic")
def apply_quotation_fcl_freight_rate_statistic_api(
    request: ApplyQuotationFclFreightRateStatistics,
    auth_response: dict = Depends(authorize_token),
):
    if auth_response.get("status_code") != 200:
        return JSONResponse(
            status_code=auth_response.get("status_code"), content=auth_response
        )

    try:
        apply_quotation_fcl_freight_rate_statistic(request)
        return JSONResponse(status_code=200, content={"success": True})
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@bramhastra.post("/apply_rd_fcl_freight_rate_statistic")
def apply_fcl_freight_rate_rd_statistic_api(
    request: ApplyRevenueDeskFclFreightStatistics,
    auth_response: dict = Depends(authorize_token),
):
    if auth_response.get("status_code") != 200:
        return JSONResponse(
            status_code=auth_response.get("status_code"), content=auth_response
        )

    try:
        apply_fcl_freight_rate_rd_statistic(request)
        return JSONResponse(status_code=200, content={"success": True})
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@bramhastra.post("/apply_shipment_fcl_freight_rate_statistic")
def apply_shipment_fcl_freight_rate_statistic_api(
    request: ApplyShipmentFclFreightRateStatistics,
    auth_response: dict = Depends(authorize_token),
):
    if auth_response.get("status_code") != 200:
        return JSONResponse(
            status_code=auth_response.get("status_code"), content=auth_response
        )
    try:
        apply_shipment_fcl_freight_rate_statistic(request)
        return JSONResponse(status_code=200, content={"success": True})
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@bramhastra.post("/apply_checkout_fcl_freight_rate_statistic")
def apply_checkout_fcl_freight_rate_statistic_api(
    request: ApplyCheckoutFclFreightRateStatistic,
    auth_response: dict = Depends(authorize_token),
):
    if auth_response.get("status_code") != 200:
        return JSONResponse(
            status_code=auth_response.get("status_code"), content=auth_response
        )
    try:
        apply_checkout_fcl_freight_rate_statistic(request)
        return JSONResponse(status_code=200, content={"success": True})
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@bramhastra.get("/get_fcl_freight_rate_charts", response_model=FclFreightRateCharts)
def get_fcl_freight_rate_charts_api(
    filters: Annotated[Json, Query()] = {},
    auth_response: dict = Depends(authorize_token),
):
    if auth_response.get("status_code") != 200:
        return JSONResponse(
            status_code=auth_response.get("status_code"), content=auth_response
        )

    try:
        response = get_fcl_freight_rate_charts(filters)
        return JSONResponse(status_code=200, content=response)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@bramhastra.get(
    "/get_fcl_freight_rate_distribution", response_model=FclFreightRateDistribution
)
async def get_fcl_freight_rate_distribution_api(
    filters: Annotated[Json, Query()] = {},
    auth_response: dict = Depends(authorize_token),
):
    if auth_response.get("status_code") != 200:
        return JSONResponse(
            status_code=auth_response.get("status_code"), content=auth_response
        )

    try:
        response = await get_fcl_freight_rate_distribution(filters)
        return JSONResponse(status_code=200, content=response)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@bramhastra.get(
    "/get_fcl_freight_rate_lifecycle", response_model=FclFreightRateLifeCycleResponse
)
async def get_fcl_freight_rate_lifecycle_api(
    filters: Annotated[Json, Query()] = {},
    auth_response: dict = Depends(authorize_token),
):
    if auth_response.get("status_code") != 200:
        return JSONResponse(
            status_code=auth_response.get("status_code"), content=auth_response
        )

    try:
        response = await get_fcl_freight_rate_lifecycle(filters)
        return JSONResponse(status_code=200, content=response)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@bramhastra.get("/get_fcl_freight_map_view_statistics", response_model=DefaultList)
def get_fcl_freight_map_view_statistics_api(
    filters: Annotated[Json, Query()] = {
        "origin": {"type": "country", "id": INDIAN_LOCATION_ID}
    },
    sort_by: str = "accuracy",
    sort_type: str = "desc",
    page_limit: int = 30,
    page: int = 1,
    auth_response: dict = Depends(authorize_token),
):
    if auth_response.get("status_code") != 200:
        return JSONResponse(
            status_code=auth_response.get("status_code"), content=auth_response
        )

    try:
        response = get_fcl_freight_map_view_statistics(
            filters, sort_by, sort_type, page_limit, page
        )
        return JSONResponse(status_code=200, content=response)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@bramhastra.get(
    "/get_fcl_freight_rate_world", response_model=FclFreightRateWorldResponse
)
async def get_fcl_freight_rate_world_api(
    auth_response: dict = Depends(authorize_token),
):
    if auth_response.get("status_code") != 200:
        return JSONResponse(
            status_code=auth_response.get("status_code"), content=auth_response
        )

    try:
        response = await get_fcl_freight_rate_world()
        return JSONResponse(status_code=200, content=response)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@bramhastra.get("/list_fcl_freight_rate_statistics", response_model=DefaultList)
async def list_fcl_freight_rate_statistics_api(
    filters: Annotated[Json, Query()] = {},
    page_limit: int = 10,
    page: int = 1,
    auth_response: dict = Depends(authorize_token),
):
    if auth_response.get("status_code") != 200:
        return JSONResponse(
            status_code=auth_response.get("status_code"), content=auth_response
        )

    try:
        response = await list_fcl_freight_rate_statistics(filters, page_limit, page)
        return JSONResponse(status_code=200, content=response)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@bramhastra.get("/list_fcl_freight_rate_request_statistics", response_model=DefaultList)
def list_fcl_freight_rate_request_statistics_api(
    filters: Annotated[Json, Query()] = {},
    page_limit: int = 10,
    page: int = 1,
    auth_response: dict = Depends(authorize_token),
):
    if auth_response.get("status_code") != 200:
        return JSONResponse(
            status_code=auth_response.get("status_code"), content=auth_response
        )

    try:
        response = list_fcl_freight_rate_request_statistics(filters, page_limit, page)
        return JSONResponse(status_code=200, content=response)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@bramhastra.get("/get_fcl_freight_port_pair_count")
def get_fcl_freight_port_pair_count_api(
    filters: Json = Query(None), auth_response: dict = Depends(authorize_token)
):
    if auth_response.get("status_code") != 200:
        return JSONResponse(
            status_code=auth_response.get("status_code"), content=auth_response
        )

    try:
        if not filters:
            return dict(port_pair_rate_count=[])
        response = get_fcl_freight_port_pair_count(filters)
        return JSONResponse(status_code=200, content=response)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )
        

@bramhastra.get("/get_fcl_freight_deviation")
def get_fcl_freight_deviation_api(
    filters: Json = Query(None), auth_response: dict = Depends(authorize_token),
    page_limit: int = 10,
    page: int = 1,
):
    if auth_response.get("status_code") != 200:
        return JSONResponse(
            status_code=auth_response.get("status_code"), content=auth_response
        )

    try:
        response = get_fcl_freight_deviation(filters,page,page_limit)
        return JSONResponse(status_code=200, content=response)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )
