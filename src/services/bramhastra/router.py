from fastapi import APIRouter, Depends, Query, Request
from services.bramhastra.interactions.apply_spot_search_fcl_freight_rate_statistic import (
    apply_spot_search_fcl_freight_rate_statistic,
)
from services.bramhastra.interactions.apply_checkout_fcl_freight_rate_statistic import (
    apply_checkout_fcl_freight_rate_statistic,
)
from services.bramhastra.interactions.apply_shipment_fcl_freight_rate_statistic import (
    apply_shipment_fcl_freight_rate_statistic,
)
from services.bramhastra.interactions.apply_fcl_freight_rate_rd_statistic import (
    apply_fcl_freight_rate_rd_statistic,
)
from services.bramhastra.interactions.apply_quotation_fcl_freight_rate_statistic import (
    apply_quotation_fcl_freight_rate_statistic,
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
from services.bramhastra.interactions.get_fcl_freight_port_pair_count import (
    get_fcl_freight_port_pair_count,
)
from services.bramhastra.interactions.get_fcl_freight_rate_differences import (
    get_fcl_freight_rate_differences,
)
from services.bramhastra.interactions.get_fcl_freight_rate_deviation import (
    get_fcl_freight_deviation,
)
from services.bramhastra.interactions.get_fcl_freight_rate_trends import (
    get_fcl_freight_rate_trends,
)
from services.bramhastra.interactions.get_fcl_freight_rate_audit_statistics import (
    get_fcl_freight_rate_audit_statistics,
)
from services.bramhastra.interactions.list_fcl_freight_recommended_trends import (
    list_fcl_freight_recommended_trends,
)
from services.bramhastra.interactions.list_fcl_freight_rate_trends import (
    list_fcl_freight_rate_trends,
)

#Air Statistics

from services.bramhastra.interactions.apply_spot_search_air_freight_rate_statistic import (
    apply_spot_search_air_freight_rate_statistic,
)
from services.bramhastra.interactions.apply_checkout_air_freight_rate_statistic import (
    apply_checkout_air_freight_rate_statistic,
)
from services.bramhastra.interactions.apply_shipment_air_freight_rate_statistic import (
    apply_shipment_air_freight_rate_statistic,
)
from services.bramhastra.interactions.apply_air_freight_rate_rd_statistic import (
    apply_air_freight_rate_rd_statistic,
)
from services.bramhastra.interactions.apply_quotation_air_freight_rate_statistic import (
    apply_quotation_air_freight_rate_statistic,
)
from services.bramhastra.interactions.get_air_freight_rate_charts import (
    get_air_freight_rate_charts,
)
from services.bramhastra.interactions.get_air_freight_rate_distribution import (
    get_air_freight_rate_distribution,
)
from services.bramhastra.interactions.get_air_freight_rate_lifecycle import (
    get_air_freight_rate_lifecycle,
)
from services.bramhastra.interactions.get_air_freight_map_view_statistics import (
    get_air_freight_map_view_statistics,
)
from services.bramhastra.interactions.get_air_freight_rate_world import (
    get_air_freight_rate_world,
)
from services.bramhastra.interactions.list_air_freight_rate_statistics import (
    list_air_freight_rate_statistics,
)
from services.bramhastra.interactions.list_air_freight_rate_request_statistics import (
    list_air_freight_rate_request_statistics,
)
from services.bramhastra.interactions.get_air_freight_port_pair_count import (
    get_air_freight_port_pair_count,
)
from services.bramhastra.interactions.get_air_freight_rate_differences import (
    get_air_freight_rate_differences,
)
from services.bramhastra.interactions.get_air_freight_rate_deviation import (
    get_air_freight_deviation,
)
from services.bramhastra.interactions.get_air_freight_rate_trends import (
    get_air_freight_rate_trends,
)
from services.bramhastra.interactions.get_air_freight_rate_audit_statistics import (
    get_air_freight_rate_audit_statistics,
)
from services.bramhastra.interactions.list_air_freight_recommended_trends import (
    list_air_freight_recommended_trends,
)
from services.bramhastra.interactions.list_air_freight_rate_trends import (
    list_air_freight_rate_trends,
)


from services.bramhastra.request_params import (
    ApplySpotSearchFclFreightRateStatistic,
    ApplyCheckoutFclFreightRateStatistic,
    ApplyShipmentFclFreightRateStatistics,
    ApplyRevenueDeskFclFreightStatistics,
    ApplyQuotationFclFreightRateStatistics,
    ApplySpotSearchAirFreightRateStatistic,
    ApplyCheckoutAirFreightRateStatistic,
    ApplyShipmentAirFreightRateStatistics,
    ApplyRevenueDeskAirFreightStatistics,
    ApplyQuotationAirFreightRateStatistics,
)
from pydantic.types import Json
from typing import Annotated
from services.bramhastra.response_models import (
    FclFreightRateCharts,
    FclFreightRateDistribution,
    FclFreightRateLifeCycleResponse,
    DefaultList,
    FclFreightRateWorldResponse,
    AirFreightRateCharts,
    AirFreightRateDistribution,
    AirFreightRateLifeCycleResponse,
    AirFreightRateWorldResponse,
)
from fastapi.responses import JSONResponse
from services.bramhastra.constants import INDIAN_LOCATION_ID
from rms_utils.auth import authorize_token
from fastapi import HTTPException
import sentry_sdk
from datetime import datetime, timedelta
from libs.rate_limiter import rate_limiter
from services.bramhastra.enums import FclParentMode, AirSources

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
def get_fcl_freight_rate_distribution_api(
    filters: Annotated[Json, Query()] = {},
    auth_response: dict = Depends(authorize_token),
):
    if auth_response.get("status_code") != 200:
        return JSONResponse(
            status_code=auth_response.get("status_code"), content=auth_response
        )

    try:
        response = get_fcl_freight_rate_distribution(filters)
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
def get_fcl_freight_rate_lifecycle_api(
    filters: Annotated[Json, Query()] = {},
    auth_response: dict = Depends(authorize_token),
):
    if auth_response.get("status_code") != 200:
        return JSONResponse(
            status_code=auth_response.get("status_code"), content=auth_response
        )

    try:
        response = get_fcl_freight_rate_lifecycle(filters)
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
    sort_by: str = None,
    sort_type: str = None,
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
def get_fcl_freight_rate_world_api(
    filters: Annotated[Json, Query()] = {},
    auth_response: dict = Depends(authorize_token),
):
    if auth_response.get("status_code") != 200:
        return JSONResponse(
            status_code=auth_response.get("status_code"), content=auth_response
        )

    try:
        response = get_fcl_freight_rate_world(filters)
        return JSONResponse(status_code=200, content=response)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@bramhastra.get("/list_fcl_freight_rate_statistics", response_model=DefaultList)
def list_fcl_freight_rate_statistics_api(
    filters: Annotated[Json, Query()] = {},
    page_limit: int = 10,
    page: int = 1,
    is_service_object_required: bool = True,
    auth_response: dict = Depends(authorize_token),
):
    if auth_response.get("status_code") != 200:
        return JSONResponse(
            status_code=auth_response.get("status_code"), content=auth_response
        )

    try:
        response = list_fcl_freight_rate_statistics(
            filters, page_limit, page, is_service_object_required
        )
        return JSONResponse(status_code=200, content=response)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@bramhastra.get("/list_air_freight_rate_statistics", response_model=DefaultList)
def list_air_freight_rate_statistics_api(
    filters: Annotated[Json, Query()] = {},
    page_limit: int = 10,
    page: int = 1,
    is_service_object_required: bool = True,
    pagination_data_required: bool = False,
    auth_response: dict = Depends(authorize_token),
):
    if auth_response.get("status_code") != 200:
        return JSONResponse(
            status_code=auth_response.get("status_code"), content=auth_response
        )
    try:
        response = list_air_freight_rate_statistics(
            filters,
            page_limit,
            page,
            is_service_object_required,
            pagination_data_required,
        )
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
    filters: Json = Query(None),
    auth_response: dict = Depends(authorize_token),
    page_limit: int = 10,
    page: int = 1,
):
    if auth_response.get("status_code") != 200:
        return JSONResponse(
            status_code=auth_response.get("status_code"), content=auth_response
        )

    try:
        response = get_fcl_freight_deviation(filters, page, page_limit)
        return JSONResponse(status_code=200, content=response)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@bramhastra.get("/get_fcl_freight_rate_trends")
def get_fcl_freight_rate_trends_api(
    filters: Annotated[Json, Query()] = {},
    auth_response: dict = Depends(authorize_token),
):
    if auth_response.get("status_code") != 200:
        return JSONResponse(
            status_code=auth_response.get("status_code"), content=auth_response
        )

    try:
        response = get_fcl_freight_rate_trends(filters)
        return JSONResponse(status_code=200, content=response)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@bramhastra.get("/get_air_freight_rate_trends")
def get_air_freight_rate_trends_api(
    filters: Annotated[Json, Query()] = {},
    auth_response: dict = Depends(authorize_token),
):
    if auth_response.get("status_code") != 200:
        return JSONResponse(
            status_code=auth_response.get("status_code"), content=auth_response
        )

    try:
        response = get_air_freight_rate_trends(filters)
        return JSONResponse(status_code=200, content=response)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@bramhastra.get("/get_fcl_freight_rate_trends_for_public", tags=["Public"])
@rate_limiter.add(max_requests=3, time_window=3600)
def get_fcl_freight_rate_trends_public_api(
    request: Request,
    filters: Annotated[Json, Query()] = {},
):
    filters["end_date"] = (datetime.utcnow() - timedelta(days=15)).date().isoformat()
    filters["mode"] = FclParentMode.supply.value

    try:
        response = get_fcl_freight_rate_trends(filters)
        return JSONResponse(status_code=200, content=response)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@bramhastra.get(
    "/get_air_freight_rate_trends_for_public",
    tags=["Public"],
    summary="gets air freight rates trend which are manual",
)
@rate_limiter.add(max_requests=10, time_window=3600)
def get_air_freight_rate_trends_public_api(
    request: Request,
    filters: Annotated[Json, Query()] = {},
):
    filters["end_date"] = (datetime.utcnow() - timedelta(days=15)).date().isoformat()
    filters["source"] = AirSources.manual.value

    try:
        response = get_air_freight_rate_trends(filters)
        return JSONResponse(status_code=200, content=response)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@bramhastra.get("/get_air_freight_rate_world")
def get_air_freight_rate_world_api(
    auth_response: dict = Depends(authorize_token),
):
    if auth_response.get("status_code") != 200:
        return JSONResponse(
            status_code=auth_response.get("status_code"), content=auth_response
        )

    try:
        response = get_air_freight_rate_world()
        return JSONResponse(status_code=200, content=response)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@bramhastra.get("/get_fcl_freight_rate_audit_statistics")
def get_fcl_freight_rate_audit_statistics_api(
    filters: Annotated[Json, Query()] = {},
    auth_response: dict = Depends(authorize_token),
):
    if auth_response.get("status_code") != 200:
        return JSONResponse(
            status_code=auth_response.get("status_code"), content=auth_response
        )

    try:
        response = get_fcl_freight_rate_audit_statistics(filters)
        return JSONResponse(status_code=200, content=response)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@bramhastra.get("/list_fcl_freight_recommended_trends", tags=["Public"])
@rate_limiter.add(max_requests=3, time_window=3600)
def list_fcl_freight_recommended_trends_api(
    request: Request,
    filters: Annotated[Json, Query()] = {},
    limit: int = 5,
    is_service_object_required: bool = False,
):
    try:
        limit = min(limit, 5)
        response = list_fcl_freight_recommended_trends(
            filters, limit, is_service_object_required
        )
        return JSONResponse(status_code=200, content=response)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@bramhastra.get("/list_fcl_freight_rate_trends")
def list_fcl_freight_rate_trends_api(
    filters: Annotated[Json, Query()] = {},
):
    try:
        response = list_fcl_freight_rate_trends(filters)
        return JSONResponse(status_code=200, content=response)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@bramhastra.get("/get_fcl_freight_rate_differences")
def get_fcl_freight_rate_differences_api(
    filters: Annotated[Json, Query()] = {},
    auth_response: dict = Depends(authorize_token),
):
    if auth_response.get("status_code") != 200:
        return JSONResponse(
            status_code=auth_response.get("status_code"), content=auth_response
        )

    try:
        response = get_fcl_freight_rate_differences(filters)
        return JSONResponse(status_code=200, content=response)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@bramhastra.get("/list_air_freight_recommended_trends", tags=["Public"])
@rate_limiter.add(max_requests=3, time_window=3600)
def list_air_freight_recommended_trends_api(
    request: Request,
    filters: Annotated[Json, Query()] = {},
    limit: int = 5,
    is_service_object_required: bool = False,
):
    try:
        limit = min(limit, 5)
        response = list_air_freight_recommended_trends(
            filters, limit, is_service_object_required
        )
        return JSONResponse(status_code=200, content=response)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )
    

@bramhastra.get("/list_air_freight_rate_trends")
def list_air_freight_rate_trends_api(
    filters: Annotated[Json, Query()] = {},
):
    try:
        response = list_air_freight_rate_trends(filters)
        return JSONResponse(status_code=200, content=response)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )
    
@bramhastra.get("/list_air_freight_rate_trends")
def list_air_freight_rate_trends_api(
    filters: Annotated[Json, Query()] = {},
):
    try:
        response = list_air_freight_rate_trends(filters)
        return JSONResponse(status_code=200, content=response)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )
    
@bramhastra.get("/list_air_freight_rate_trends")
def list_air_freight_rate_trends_api(
    filters: Annotated[Json, Query()] = {},
):
    try:
        response = list_air_freight_rate_trends(filters)
        return JSONResponse(status_code=200, content=response)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )
    
@bramhastra.post("/apply_air_freight_rate_rd_statistic")
def apply_air_freight_rate_rd_statistic_api(
    request: ApplyRevenueDeskAirFreightStatistics,
    auth_response: dict = Depends(authorize_token),
):
    if auth_response.get("status_code") != 200:
        return JSONResponse(
            status_code=auth_response.get("status_code"), content=auth_response
        )

    try:
        apply_air_freight_rate_rd_statistic(request)
        return JSONResponse(status_code=200, content={"success": True})
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )
    
@bramhastra.post("/apply_spot_search_air_freight_rate_statistic")
def apply_spot_search_air_freight_rate_statistic_api(
    request: ApplySpotSearchAirFreightRateStatistic,
    auth_response: dict = Depends(authorize_token),
):
    if auth_response.get("status_code") != 200:
        return JSONResponse(
            status_code=auth_response.get("status_code"), content=auth_response
        )

    try:
        apply_spot_search_air_freight_rate_statistic(request)
        return JSONResponse(status_code=200, content={"success": True})
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@bramhastra.post("/apply_checkout_air_freight_rate_statistic")
def apply_checkout_air_freight_rate_statistic_api(
    request: ApplyCheckoutAirFreightRateStatistic,
    auth_response: dict = Depends(authorize_token),
):
    if auth_response.get("status_code") != 200:
        return JSONResponse(
            status_code=auth_response.get("status_code"), content=auth_response
        )

    try:
        apply_checkout_air_freight_rate_statistic(request)
        return JSONResponse(status_code=200, content={"success": True})
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )
    
@bramhastra.post("/apply_shipment_air_freight_rate_statistic")
def apply_shipment_air_freight_rate_statistic_api(
    request: ApplyShipmentAirFreightRateStatistics,
    auth_response: dict = Depends(authorize_token),
):
    if auth_response.get("status_code") != 200:
        return JSONResponse(
            status_code=auth_response.get("status_code"), content=auth_response
        )

    try:
        apply_shipment_air_freight_rate_statistic(request)
        return JSONResponse(status_code=200, content={"success": True})
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )
    
@bramhastra.post("/apply_quotation_air_freight_rate_statistic")
def apply_quotation_air_freight_rate_statistic_api(
    request: ApplyQuotationAirFreightRateStatistics,
    auth_response: dict = Depends(authorize_token),
):
    if auth_response.get("status_code") != 200:
        return JSONResponse(
            status_code=auth_response.get("status_code"), content=auth_response
        )

    try:
        apply_quotation_air_freight_rate_statistic(request)
        return JSONResponse(status_code=200, content={"success": True})
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )
    
@bramhastra.get("/list_air_freight_rate_request_statistics", response_model=DefaultList)
def list_air_freight_rate_request_statistics_api(
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
        response = list_air_freight_rate_request_statistics(filters, page_limit, page)
        return JSONResponse(status_code=200, content=response)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )
    
@bramhastra.get("/get_air_freight_rate_charts", response_model=AirFreightRateCharts)
def get_air_freight_rate_charts_api(
    filters: Annotated[Json, Query()] = {},
    auth_response: dict = Depends(authorize_token),
):
    if auth_response.get("status_code") != 200:
        return JSONResponse(
            status_code=auth_response.get("status_code"), content=auth_response
        )

    try:
        response = get_air_freight_rate_charts(filters)
        return JSONResponse(status_code=200, content=response)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )

@bramhastra.get(
    "/get_air_freight_rate_distribution", response_model=AirFreightRateDistribution
)
def get_air_freight_rate_distribution_api(
    filters: Annotated[Json, Query()] = {},
    auth_response: dict = Depends(authorize_token),
):
    if auth_response.get("status_code") != 200:
        return JSONResponse(
            status_code=auth_response.get("status_code"), content=auth_response
        )

    try:
        response = get_air_freight_rate_distribution(filters)
        return JSONResponse(status_code=200, content=response)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )

@bramhastra.get(
    "/get_air_freight_rate_lifecycle", response_model=AirFreightRateLifeCycleResponse
)
def get_air_freight_rate_lifecycle_api(
    filters: Annotated[Json, Query()] = {},
    auth_response: dict = Depends(authorize_token),
):
    if auth_response.get("status_code") != 200:
        return JSONResponse(
            status_code=auth_response.get("status_code"), content=auth_response
        )

    try:
        response = get_air_freight_rate_lifecycle(filters)
        return JSONResponse(status_code=200, content=response)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )
    
@bramhastra.get("/get_air_freight_map_view_statistics", response_model=DefaultList)
def get_air_freight_map_view_statistics_api(
    filters: Annotated[Json, Query()] = {
        "origin": {"type": "country", "id": INDIAN_LOCATION_ID}
    },
    page_limit: int = 30,
    page: int = 1,
    auth_response: dict = Depends(authorize_token),
):
    if auth_response.get("status_code") != 200:
        return JSONResponse(
            status_code=auth_response.get("status_code"), content=auth_response
        )

    try:
        response = get_air_freight_map_view_statistics(
            filters, page_limit, page
        )
        return JSONResponse(status_code=200, content=response)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )
    
@bramhastra.get("/get_air_freight_rate_audit_statistics")
def get_air_freight_rate_audit_statistics_api(
    filters: Annotated[Json, Query()] = {},
    auth_response: dict = Depends(authorize_token),
):
    if auth_response.get("status_code") != 200:
        return JSONResponse(
            status_code=auth_response.get("status_code"), content=auth_response
        )

    try:
        response = get_air_freight_rate_audit_statistics(filters)
        return JSONResponse(status_code=200, content=response)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )
    

@bramhastra.get("/get_air_freight_rate_differences")
def get_air_freight_rate_differences_api(
    filters: Annotated[Json, Query()] = {},
    auth_response: dict = Depends(authorize_token),
):
    if auth_response.get("status_code") != 200:
        return JSONResponse(
            status_code=auth_response.get("status_code"), content=auth_response
        )

    try:
        response = get_air_freight_rate_differences(filters)
        return JSONResponse(status_code=200, content=response)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )
    
@bramhastra.get("/get_air_freight_deviation")
def get_air_freight_deviation_api(
    filters: Json = Query(None),
    auth_response: dict = Depends(authorize_token),
    page_limit: int = 10,
    page: int = 1,
):
    if auth_response.get("status_code") != 200:
        return JSONResponse(
            status_code=auth_response.get("status_code"), content=auth_response
        )

    try:
        response = get_air_freight_deviation(filters, page, page_limit)
        return JSONResponse(status_code=200, content=response)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )
    
@bramhastra.get("/get_air_freight_port_pair_count")
def get_air_freight_port_pair_count_api(
    filters: Json = Query(None), auth_response: dict = Depends(authorize_token)
):
    if auth_response.get("status_code") != 200:
        return JSONResponse(
            status_code=auth_response.get("status_code"), content=auth_response
        )

    try:
        if not filters:
            return dict(port_pair_rate_count=[])
        response = get_air_freight_port_pair_count(filters)
        return JSONResponse(status_code=200, content=response)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )