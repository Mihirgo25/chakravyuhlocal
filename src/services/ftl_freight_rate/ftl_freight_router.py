from fastapi import APIRouter, Depends
from rms_utils.auth import authorize_token
from fastapi.responses import JSONResponse
import sentry_sdk
from libs.json_encoder import json_encoder
from fastapi import HTTPException
from datetime import datetime
from services.ftl_freight_rate.interactions.get_estimated_ftl_freight_rate import (
    get_estimated_ftl_freight_rate,
)
from services.ftl_freight_rate.interactions.list_ftl_freight_rule_sets import (
    list_ftl_rule_set_data,
)
from services.ftl_freight_rate.interactions.create_ftl_freight_rate_rule_set import (
    create_ftl_rule_set_data,
)
from services.ftl_freight_rate.interactions.update_ftl_freight_rate_rule_set import (
    update_ftl_rule_set_data,
)
from services.ftl_freight_rate.interactions.list_trucks import list_trucks_data
from services.ftl_freight_rate.interactions.create_truck import create_truck_data
from services.ftl_freight_rate.interactions.update_truck import update_truck_data
from services.ftl_freight_rate.ftl_params import *
from services.ftl_freight_rate.interactions.create_fuel_data import create_fuel_data
from services.ftl_freight_rate.interactions.get_truck_detail import get_truck_detail

from services.ftl_freight_rate.interactions.create_ftl_freight_rate import create_ftl_freight_rate
from services.ftl_freight_rate.interactions.create_ftl_freight_rate_request import create_ftl_freight_rate_request
from services.ftl_freight_rate.interactions.update_ftl_freight_rate_request import update_ftl_freight_rate_request
from services.ftl_freight_rate.interactions.create_ftl_freight_rate_feedback import create_ftl_freight_rate_feedback
from services.ftl_freight_rate.interactions.delete_ftl_freight_rate_feedback import delete_ftl_freight_rate_feedback
from services.ftl_freight_rate.interactions.list_ftl_freight_rate_requests import list_ftl_freight_rate_requests;
from services.ftl_freight_rate.interactions.list_ftl_freight_rates import list_ftl_freight_rates
from services.ftl_freight_rate.interactions.update_ftl_freight_rate import update_ftl_freight_rate
from services.ftl_freight_rate.interactions.create_ftl_freight_rate_not_available import create_ftl_freight_rate_not_available
from services.ftl_freight_rate.interactions.delete_ftl_freight_rate_request import delete_ftl_freight_rate_request
from services.ftl_freight_rate.interactions.update_ftl_freight_rate_platform_prices import update_ftl_freight_rate_platform_prices
from services.ftl_freight_rate.interactions.delete_ftl_freight_rate import delete_ftl_freight_rate
from services.ftl_freight_rate.interactions.get_ftl_freight_rate_addition_frequency import get_ftl_freight_rate_addition_frequency
from services.ftl_freight_rate.interactions.get_ftl_freight_rate_visibility import get_ftl_freight_rate_visibility
from services.ftl_freight_rate.interactions.get_ftl_freight_rate import get_ftl_freight_rate
from services.ftl_freight_rate.interactions.list_ftl_freight_rate_feedbacks import list_ftl_freight_rate_feedbacks
from services.ftl_freight_rate.interactions.create_ftl_freight_rate_bulk_operation import create_ftl_freight_rate_bulk_operation
from services.ftl_freight_rate.interactions.get_ftl_freight_rate_min_max_validity_dates import get_ftl_freight_rate_min_max_validity_dates
from services.ftl_freight_rate.interactions.get_ftl_freight_rate_cards import get_ftl_freight_rate_cards
from services.ftl_freight_rate.interactions.extend_ftl_freight_rates import extend_ftl_freight_rate
ftl_freight_router = APIRouter()


@ftl_freight_router.get("/get_estimated_ftl_freight_rate")
def get_estimated_ftl_freight_rate_api(
    origin_location_id: str = None,
    destination_location_id: str = None,
    trip_type: str = "one_way",
    truck_type: str = None,
    commodity: str = None,
    weight: str = None,
    truck_body_type: str = None,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    if weight:
        weight = float(weight)

    data = get_estimated_ftl_freight_rate(
        origin_location_id,
        destination_location_id,
        trip_type,
        commodity,
        weight,
        truck_type,
        truck_body_type
    )
    data = json_encoder(data)
    return JSONResponse(status_code=200, content=data)


@ftl_freight_router.post("/create_fuel_data")
def create_fuel_datas(request: CreateFuelData, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = create_fuel_data(request.dict(exclude_none=False))
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@ftl_freight_router.get("/list_ftl_freight_rate_rule_sets")
def list_ftl_rule_set(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    sort_by: str = "created_at",
    sort_type: str = "asc",
    pagination_data_required: bool = False,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = list_ftl_rule_set_data(
            filters, page_limit, page, sort_by, sort_type, pagination_data_required
        )
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@ftl_freight_router.post("/create_ftl_freight_rate_rule_set")
def create_ftl_rule_set(
    request: CreateFtlRuleSet, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
    try:
        data = create_ftl_rule_set_data(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@ftl_freight_router.post("/update_ftl_freight_rate_rule_set")
def update_ftl_rule_set(
    request: UpdateFtlRuleSet, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = update_ftl_rule_set_data(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@ftl_freight_router.get("/list_trucks")
def list_trucks(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    sort_by: str = "created_at",
    sort_type: str = "asc",
    pagination_data_required: bool = True,
):
    try:
        data = list_trucks_data(
            filters, page_limit, page, sort_by, sort_type, pagination_data_required
        )
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@ftl_freight_router.post("/create_truck")
def create_truck(request: CreateTruck, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
    try:
        data = create_truck_data(request.dict())
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@ftl_freight_router.post("/update_truck")
def update_truck(request: UpdateTruck, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = update_truck_data(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@ftl_freight_router.get("/get_truck_detail")
def get_truck_data(
    truck_id: str = None,
    truck_name: str = None,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        request = {"id": truck_id, "truck_name": truck_name}
        data = get_truck_detail(request)
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )

@ftl_freight_router.post("/create_ftl_freight_rate")
def create_ftl_freight_rate_api(request: CreateFtlFreightRate, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        rate = create_ftl_freight_rate(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
            )

@ftl_freight_router.post("/create_ftl_freight_rate_request")
def create_ftl_freight_rate_request_api(
    request: CreateFtlFreightRateRequest, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = create_ftl_freight_rate_request(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@ftl_freight_router.post("/update_ftl_freight_rate_request")
def update_ftl_freight_rate_request_api(
    request: UpdateFtlFreightRateRequest, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = update_ftl_freight_rate_request(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )

@ftl_freight_router.post("/create_ftl_freight_rate_feedback")
def create_ftl_freight_rate_feedback_api(request: CreateFtlFreightRateFeedback, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        rate_id = create_ftl_freight_rate_feedback(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(rate_id))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@ftl_freight_router.post("/delete_ftl_freight_rate_feedback")
def delete_ftl_freight_rates_feedback_api(request: DeleteFtlFreightRateFeedback, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        delete_rate = delete_ftl_freight_rate_feedback(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(delete_rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@ftl_freight_router.get("list_ftl_freight_rate_requests")
def list_ftl_freight_rate_request_api(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    sort_by: str = "created_at",
    sort_type: str = "asc",
    is_stats_required: bool = False,
    spot_search_details_required: bool = False,
    performed_by_id = None,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = list_ftl_freight_rate_requests(
            filters, page_limit, page, sort_by, sort_type,is_stats_required,spot_search_details_required,performed_by_id
        )
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )

@ftl_freight_router.get("/list_ftl_freight_rates")
def list_ftl_freight_rates_api(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    return_query : bool = False,
    pagination_data_required: bool = False,
    all_rates_for_cogo_assured: bool = False,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = list_ftl_freight_rates(filters, page_limit, page, return_query, pagination_data_required, all_rates_for_cogo_assured)
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@ftl_freight_router.post("/update_ftl_freight_rate")
def update_ftl_freight_rate_api(request: UpdateFtlFreightRate, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        rate = update_ftl_freight_rate(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@ftl_freight_router.post("/delete_ftl_freight_rate_request")
def delete_ftl_freight_rate_request_api(request: DeleteFtlFreightRateRequest, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        delete_rate = delete_ftl_freight_rate_request(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(delete_rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@ftl_freight_router.post("/create_ftl_freight_rate_not_available")
def create_ftl_freight_rate_not_available_data(request: CreateFtlFreightRateNotAvailable, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        rate = create_ftl_freight_rate_not_available(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@ftl_freight_router.post("/update_ftl_freight_rate_platform_prices")
def update_ftl_freight_rate_platform_prices_api(request:UpdateFtlFreightRatePlatformPrices, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        rate = update_ftl_freight_rate_platform_prices(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@ftl_freight_router.post("/delete_ftl_freight_rate")
def delete_ftl_freight_rate_api(request: DeleteFtlFreightRate, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        delete_rate = delete_ftl_freight_rate(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(delete_rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@ftl_freight_router.get("/get_ftl_freight_rate_addition_frequency")
def get_ftl_freight_rate_addition_frequency_api(
    group_by: str,
    filters: str = None,
    sort_type: str = 'desc',
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = get_ftl_freight_rate_addition_frequency( group_by, filters, sort_type)
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@ftl_freight_router.get("/get_ftl_freight_rate_visibility")
def get_ftl_freight_rate_visibility_api(
    service_provider_id: str,
    origin_location_id: str = None,
    destination_location_id: str = None,
    from_date: datetime = None,
    to_date: datetime = None,
    rate_id: str = None,
    truck_type: str = None,
    commodity: str = None,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    request = {
        'service_provider_id' : service_provider_id,
        'origin_location_id': origin_location_id,
        'destination_location_id': destination_location_id,
        'from_date': from_date,
        'to_date': to_date,
        'rate_id': rate_id,
        'truck_type': truck_type,
        'commodity': commodity
    }
    try:
        data = get_ftl_freight_rate_visibility(request)
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@ftl_freight_router.get("/get_ftl_freight_rate")
def get_ftl_freight_rate_api(origin_location_id: str = None,destination_location_id: str = None, truck_type: str = None, truck_body_type: str = None, transit_time: str = None, detention_free_time: str = None, commodity: str = None, trip_type: str = None, service_provider_id: str = None, importer_exporter_id: str = None, unit: str = None, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        request = {
            'origin_location_id' : origin_location_id,
            'destination_location_id': destination_location_id,
            'truck_type':truck_type,
            'transit_time':transit_time,
            'detention_free_time':detention_free_time,
            'commodity': commodity,
            'trip_type': trip_type,
            'service_provider_id': service_provider_id,
            'importer_exporter_id': importer_exporter_id,
            'unit': unit,
            'truck_body_type': truck_body_type
        }
        rate = get_ftl_freight_rate(request)
        return JSONResponse(status_code=200, content=jsonable_encoder(rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@ftl_freight_router.get("/list_ftl_freight_rate_feedbacks")
def list_ftl_freight_rate_feedbacks_api(
    filters: str = None,
    spot_search_details_required: bool = False,
    page_limit: int = 10,
    page: int = 1,
    performed_by_id: str = None,
    is_stats_required: bool = True,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        data = list_ftl_freight_rate_feedbacks(filters, spot_search_details_required, page_limit, page, performed_by_id, is_stats_required)
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })



@ftl_freight_router.post("/create_ftl_freight_rate_bulk_operation")
def create_ftl_freight_rate_bulk_operation_data(request:CreateBulkOperation, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data=create_ftl_freight_rate_bulk_operation(request.dict(exclude_none=True))
        return JSONResponse(content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@ftl_freight_router.get("/get_ftl_freight_rate_min_max_validity_dates")
def get_ftl_freight_rate_min_max_validity_dates_api(
    shipment_id: str,
    importer_exporter_id: str,
    trip_type: str,
    origin_location_id: str = None,
    destination_location_id: str = None,
    commodity: str = None,
    cargo_readiness_date: datetime = None,
    preferred_currency: str = "USD",
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    request = {
        'shipment_id' : shipment_id,
        'origin_location_id': origin_location_id,
        'destination_location_id': destination_location_id,
        'trip_type': trip_type,
        'commodity': commodity,
        'importer_exporter_id': importer_exporter_id,
        'cargo_readiness_date': cargo_readiness_date,
        'preferred_currency': preferred_currency
    }
    try:
        data = get_ftl_freight_rate_min_max_validity_dates(request)
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@ftl_freight_router.get("/get_ftl_freight_rate_cards")
def get_ftl_freight_rate_cards_api(
    trip_type: str,
    origin_location_id: str = None,
    origin_location_type: str = None,
    origin_city_id: str = None,
    origin_country_id:str = None,
    destination_location_id: str = None,
    destination_location_type: str = None,
    destination_city_id: str = None,
    destination_country_id: str = None ,
    truck_type: str = None,
    break_point_location_ids: str = None,
    weight: float = None,
    volume: float = None,
    commodity:str = None,
    importer_exporter_id: str = None,
    trucks_count:int = None,
    additional_services: str = None,
    include_confirmed_inventory_rates: bool = False,
    include_additional_response_data:bool=False,
    cargo_readiness_date: str = None,
    load_selection_type:str = None,
    predicted_rate: bool = True,
    resp: dict = Depends(authorize_token)):

    try:
        cargo_readiness_date = datetime.fromisoformat(cargo_readiness_date).date()
    except:
        cargo_readiness_date = datetime.now().date()

    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        request = {
                        'trip_type':trip_type,
                        'origin_location_id': origin_location_id,
                        'origin_location_type': origin_location_type,
                        'origin_city_id': origin_city_id,
                        'origin_country_id': origin_country_id,
                        'destination_location_id': destination_location_id,
                        'destination_location_type': destination_location_type,
                        'destination_city_id': destination_city_id,
                        'destination_country_id':destination_country_id,
                        'truck_type': truck_type,
                        'break_point_location_ids': break_point_location_ids,
                        'weight': weight,
                        'volume': volume,
                        'commodity': commodity,
                        'importer_exporter_id': importer_exporter_id,
                        'trucks_count': trucks_count,
                        'additional_services': additional_services,
                        'include_confirmed_inventory_rates': include_confirmed_inventory_rates,
                        'include_additional_response_data': include_additional_response_data,
                        'cargo_readiness_date': cargo_readiness_date,
                        'load_selection_type': load_selection_type,
                        'predicted_rate':predicted_rate
        }
        list = get_ftl_freight_rate_cards(request)
        return JSONResponse(status_code=200, content=jsonable_encoder(list))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })


@ftl_freight_router.post("/extend_ftl_freight_rates")
def extend_ftl_freight_rates_data(request:ExtendFtlFreightRates, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data=extend_ftl_freight_rate(request.dict(exclude_none=True))
        return JSONResponse(content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
