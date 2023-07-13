from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from libs.json_encoder import json_encoder
import traceback
from rms_utils.auth import authorize_token
import sentry_sdk
from fastapi import HTTPException, Query
from typing import List, Union
from params import CreateRateSheet, UpdateRateSheet



from services.haulage_freight_rate.interactions.get_estimated_haulage_freight_rate import (
    haulage_rate_calculator,
)
from services.haulage_freight_rate.interactions.get_haulage_freight_rate import (
    get_haulage_freight_rate,
)
from services.haulage_freight_rate.interactions.list_haulage_freight_rate_requests import (
    list_haulage_freight_rate_requests,
)
from services.haulage_freight_rate.interactions.list_haulage_freight_rates import (
    list_haulage_freight_rates,
)
from services.haulage_freight_rate.interactions.create_haulage_freight_rate_request import (
    create_haulage_freight_rate_request,
)
from services.haulage_freight_rate.interactions.delete_haulage_freight_rate_request import (
    delete_haulage_freight_rate_request,
)
from services.haulage_freight_rate.interactions.create_haulage_freight_rate_feedback import (
    create_haulage_freight_rate_feedback,
)
from services.haulage_freight_rate.interactions.get_haulage_freight_rate_frequency_addition import (
    get_haulage_freight_rate_addition_frequency,
)
from services.haulage_freight_rate.interactions.update_haulage_freight_rate_platform_prices import (
    update_haulage_freight_rate_platform_prices,
)
from services.haulage_freight_rate.interactions.create_haulage_freight_rate_not_available import (
    create_haulage_freight_rate_not_available,
)
from services.haulage_freight_rate.interactions.get_haulage_freight_rate_visibility import (
    get_haulage_freight_rate_visibility,
)
from services.haulage_freight_rate.interactions.get_haulage_freight_rate_cards import (
    get_haulage_freight_rate_cards,
)
from services.haulage_freight_rate.interactions.delete_haulage_freight_rate import (
    delete_haulage_freight_rate,
)
from services.haulage_freight_rate.interactions.create_haulage_freight_rate import (
    create_haulage_freight_rate,
)
from services.haulage_freight_rate.interactions.update_haulage_freight_rate import (
    update_haulage_freight_rate,
)
from services.haulage_freight_rate.haulage_params import *
from services.haulage_freight_rate.interactions.list_haulage_freight_rate_feedback import (
    list_haulage_freight_rate_feedbacks,
)
from services.haulage_freight_rate.interactions.delete_haulage_freight_rate_feedback import (
    delete_haulage_freight_rate_feedback,
)
from services.haulage_freight_rate.interactions.create_haulage_freight_rate_bulk_operation import (
    create_haulage_freight_rate_bulk_operation,
)
from services.rate_sheet.interactions.create_rate_sheet import create_rate_sheet
from services.rate_sheet.interactions.update_rate_sheet import update_rate_sheet
from services.rate_sheet.interactions.list_rate_sheets import list_rate_sheets
from services.rate_sheet.interactions.list_rate_sheet_stats import list_rate_sheet_stats

haulage_freight_router = APIRouter()


@haulage_freight_router.get("/get_estimated_haulage_freight_rate")
def get_haulage_freight_rates(
    origin_location_id: str,
    destination_location_id: str,
    commodity: str = None,
    containers_count: int = None,
    container_type: str = None,
    container_size: str = None,
    cargo_weight_per_container: float = None,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = haulage_rate_calculator(
            origin_location_id,
            destination_location_id,
            commodity,
            containers_count,
            container_type,
            container_size,
            cargo_weight_per_container,
        )
        data = json_encoder(data)
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@haulage_freight_router.get("/get_haulage_freight_rate")
def get_haulage_freight_rate_data(
    origin_location_id: str = None,
    destination_location_id: str = None,
    commodity: str = None,
    containers_count: int = None,
    container_type: str = None,
    container_size: str = None,
    cargo_weight_per_container: float = None,
    haulage_type: str = None,
    service_provider_id: str = None,
    importer_exporter_id: str = None,
    shipping_line_id: str = None,
    transport_modes: Union[List[str], None] = Query(None),
    trip_type: str = None,
    transit_time: int = None,
    detention_free_time: int = None,
    trailer_type: str = None,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    request = {
        "origin_location_id": origin_location_id,
        "destination_location_id": destination_location_id,
        "commodity": commodity,
        "containers_count": containers_count,
        "container_type": container_type,
        "container_size": container_size,
        "cargo_weight_per_container": cargo_weight_per_container,
        "haulage_type": haulage_type,
        "service_provider_id": service_provider_id,
        "importer_exporter_id": importer_exporter_id,
        "shipping_line_id": shipping_line_id,
        "transport_modes": transport_modes,
        "trip_type": trip_type,
        "transit_time": transit_time,
        "detention_free_time": detention_free_time,
        "trailer_type": trailer_type,
    }

    try:
        data = get_haulage_freight_rate(request)
        data = json_encoder(data)
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@haulage_freight_router.post("/create_haulage_freight_rate")
def create_haulage_freight_rate_func(
    request: CreateHaulageFreightRate, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        rate = create_haulage_freight_rate(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(rate))
    except HTTPException as e:
        raise e
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "traceback": traceback.print_exc(),
            },
        )


@haulage_freight_router.post("/update_haulage_freight_rate")
def update_haulage_freight_rate_func(
    request: UpdateHaulageFreightRate, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
    try:
        rate = update_haulage_freight_rate(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(rate))
    except HTTPException as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@haulage_freight_router.get("/list_haulage_freight_rate_feedbacks")
def list_haulage_freight_rate_feedbacks_data(
    filters: str = None,
    spot_search_details_required: bool = False,
    page_limit: int = 10,
    page: int = 1,
    performed_by_id: str = None,
    is_stats_required: bool = True,
    booking_details_required: bool = False,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = list_haulage_freight_rate_feedbacks(
            filters,
            spot_search_details_required,
            page_limit,
            page,
            performed_by_id,
            is_stats_required,
            booking_details_required,
        )
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@haulage_freight_router.post("/create_haulage_freight_rate_feedback")
def create_haualge_freight_rate_feedback_data(
    request: CreateHaulageFreightRateFeedback, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = create_haulage_freight_rate_feedback(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@haulage_freight_router.post("/delete_haulage_freight_rate_feedback")
def delete_haulage_freight_rates_feedback(
    request: DeleteHaulageFreightRateFeedback, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
    try:
        delete_rate = delete_haulage_freight_rate_feedback(
            request.dict(exclude_none=True)
        )
        return JSONResponse(status_code=200, content=json_encoder(delete_rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@haulage_freight_router.get("/list_haulage_freight_rate_requests")
def list_haulage_freight_rate_requests_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    performed_by_id: str = None,
    is_stats_required: bool = True,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = list_haulage_freight_rate_requests(
            filters, page_limit, page, performed_by_id, is_stats_required
        )
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@haulage_freight_router.get("/list_haulage_freight_rates")
def list_haulage_freight_rates_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    return_query: str = None,
    pagination_data_required: bool = True,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = list_haulage_freight_rates(
            filters, page_limit, page, return_query, pagination_data_required
        )
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@haulage_freight_router.post("/create_haulage_freight_rate_request")
def create_haualge_freight_rate_request_data(
    request: CreateHaulageFreightRateRequest, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = create_haulage_freight_rate_request(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@haulage_freight_router.post("/delete_haulage_freight_rate_request")
def delete_haulage_freight_rates_request(
    request: DeleteHaulageFreightRateRequest, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        delete_rate = delete_haulage_freight_rate_request(
            request.dict(exclude_none=True)
        )
        return JSONResponse(status_code=200, content=json_encoder(delete_rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@haulage_freight_router.get("/get_haulage_freight_rate_addition_frequency")
def get_haulage_freight_rate_addition_frequency_data(
    group_by: str,
    filters: str = None,
    sort_type: str = "desc",
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = get_haulage_freight_rate_addition_frequency(group_by, filters, sort_type)
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@haulage_freight_router.post("/update_haulage_freight_rate_platform_prices")
def update_haulage_freight_rate_platform_prices_data(
    request: UpdateHaulageFreightRatePlatformPrices,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = update_haulage_freight_rate_platform_prices(
            request.dict(exclude_none=False)
        )
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@haulage_freight_router.get("/get_haulage_freight_rate_visibility")
def get_haulage_freight_rate_visibility_data(
    service_provider_id: str,
    origin_location_id: str = None,
    destination_location_id: str = None,
    rate_id: str = None,
    container_size: str = None,
    container_type: str = None,
    commodity: str = None,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    request = {
        "service_provider_id": service_provider_id,
        "origin_location_id": origin_location_id,
        "destination_location_id": destination_location_id,
        "rate_id": rate_id,
        "container_size": container_size,
        "container_type": container_type,
        "commodity": commodity,
    }
    try:
        data = get_haulage_freight_rate_visibility(request)
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@haulage_freight_router.post("/create_haulage_freight_rate_not_available")
def create_haulage_freight_rate_not_available_data(
    request: CreateHaulageFreightRateNotAvailable, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = create_haulage_freight_rate_not_available(
            request.dict(exclude_none=False)
        )
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@haulage_freight_router.get("/get_haulage_freight_rate_cards")
def get_haulage_freight_rate_cards_data(
    container_size: str,
    container_type: str,
    containers_count: int,
    origin_location_id: str = None,
    destination_location_id: str = None,
    origin_city_id: str = None,
    destination_city_id: str = None,
    origin_country_id: str = None,
    destination_country_id: str = None,
    commodity: str = None,
    shipping_line_id: str = None,
    haulage_type: str = None,
    transport_mode: str = None,
    importer_exporter_id: str = None,
    cargo_weight_per_container: int = None,
    additional_services: Union[List[str], None] = Query(None),
    include_confirmed_inventory_rates: bool = False,
    include_additional_response_data: bool = False,
    trip_type: str = None,
    predicted_rate: bool = False,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    request = {
        "container_size": container_size,
        "container_type": container_type,
        "containers_count": containers_count,
        "origin_location_id": origin_location_id,
        "destination_location_id": destination_location_id,
        "origin_city_id": origin_city_id,
        "destination_city_id": destination_city_id,
        "origin_country_id": origin_country_id,
        "destination_country_id": destination_country_id,
        "commodity": commodity,
        "shipping_line_id": shipping_line_id,
        "haulage_type": haulage_type,
        "transport_mode": transport_mode,
        "importer_exporter_id": importer_exporter_id,
        "cargo_weight_per_container": cargo_weight_per_container,
        "additional_services": additional_services,
        "include_confirmed_inventory_rates": include_confirmed_inventory_rates,
        "include_additional_response_data": include_additional_response_data,
        "trip_type": trip_type,
        "predicted_rate": predicted_rate,
    }
    try:
        data = get_haulage_freight_rate_cards(request)
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@haulage_freight_router.post("/delete_haulage_freight_rate")
def delete_haulage_freight_rate_api(
    request: DeleteHaulageFreightRate, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = delete_haulage_freight_rate(request.dict(exclude_none=False))
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@haulage_freight_router.post("/create_haulage_freight_rate_bulk_operation")
def create_haulage_freight_rate_bulk_operation_api(
    request: CreateHaulageFreightRateBulkOperation,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = create_haulage_freight_rate_bulk_operation(
            request.dict(exclude_none=False)
        )
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        print(e)
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@haulage_freight_router.post("/create_haulage_freight_rate_sheet")
def create_rate_sheet_api(request: CreateRateSheet, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        rate_sheet = create_rate_sheet(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(rate_sheet))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@haulage_freight_router.post("/update_haulage_freight_rate_sheet")
def update_rate_sheet_api(request: UpdateRateSheet, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]

    try:
        rate_sheet =update_rate_sheet(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(rate_sheet))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@haulage_freight_router.get("/list_haulage_freight_rate_sheets")
def list_rate_sheets_api(
    filters: str = None,
    stats_required: bool = True,
    page: int = 1,
    page_limit: int = 10,
    sort_by: str = 'created_at',
    sort_type: str = 'desc',
    pagination_data_required:  bool = True,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        response = list_rate_sheets(
            filters, stats_required, page, page_limit,sort_by, sort_type, pagination_data_required
        )
        return JSONResponse(status_code=200, content=response)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@haulage_freight_router.get("/list_haulage_freight_rate_sheet_stats")
def list_rates_sheet_stats_api(
    filters: str = None,
    service_provider_id: str = None,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        response = list_rate_sheet_stats(
            filters, service_provider_id
        )
        return JSONResponse(status_code=200, content=response)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
    

@haulage_freight_router.post("/create_trailer_freight_rate_sheet")
def create_rate_sheet_api(request: CreateRateSheet, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        rate_sheet = create_rate_sheet(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(rate_sheet))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@haulage_freight_router.post("/update_trailer_freight_rate_sheet")
def update_rate_sheet_api(request: UpdateRateSheet, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]

    try:
        rate_sheet =update_rate_sheet(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(rate_sheet))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@haulage_freight_router.get("/list_trailer_freight_rate_sheets")
def list_rate_sheets_api(
    filters: str = None,
    stats_required: bool = True,
    page: int = 1,
    page_limit: int = 10,
    sort_by: str = 'created_at',
    sort_type: str = 'desc',
    pagination_data_required:  bool = True,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        response = list_rate_sheets(
            filters, stats_required, page, page_limit,sort_by, sort_type, pagination_data_required
        )
        return JSONResponse(status_code=200, content=response)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@haulage_freight_router.get("/list_trailer_freight_rate_sheet_stats")
def list_rates_sheet_stats_api(
    filters: str = None,
    service_provider_id: str = None,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        response = list_rate_sheet_stats(
            filters, service_provider_id
        )
        return JSONResponse(status_code=200, content=response)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })