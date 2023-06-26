
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from params import *
import traceback
from rms_utils.auth import authorize_token
import sentry_sdk
from fastapi import Query
from fastapi import HTTPException
from services.haulage_freight_rate.interactions.get_estimated_haulage_freight_rate import (
    haulage_rate_calculator,
)
from services.haulage_freight_rate.interactions.get_haulage_freight_rate import (
    get_haulage_freight_rate,
)
from services.haulage_freight_rate.interactions.list_haulage_freight_rate_requests import (
    list_haulage_freight_rate_requests,
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

from typing import List,Union

haulage_freight_router = APIRouter()
from services.haulage_freight_rate.interactions.create_haulage_freight_rate import create_haulage_freight_rate
from services.haulage_freight_rate.interactions.update_haulage_freight_rate import update_haulage_freight_rate
from services.haulage_freight_rate.haulage_params import *
from services.haulage_freight_rate.interactions.list_haulage_freight_rate_feedback import list_haulage_freight_rate_feedbacks
from services.haulage_freight_rate.interactions.delete_haulage_freight_rate_feedback import delete_haulage_freight_rate_feedback


@haulage_freight_router.get("/get_estimated_haulage_freight_rate")
def get_haulage_freight_rate(
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
        data = jsonable_encoder(data)
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@haulage_freight_router.get("/get_haulage_freight_rate")
def get_haulage_freight_rate(
    origin_location_id: str,
    destination_location_id: str,
    commodity: str = None,
    containers_count: int = None,
    container_type: str = None,
    container_size: str = None,
    cargo_weight_per_container: float = None,
    haulage_type: str = None,
    service_provider_id: str = None,
    importer_exporter_id: str = None,
    shipping_line_id: str = None,
    transport_modes: Union[List[str],None]= Query(None),
    trip_type: str = None,
    transit_time: int = 12,
    detention_free_time: int = 1,
    trailer_type: str = None,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = get_haulage_freight_rate(
            origin_location_id,
            destination_location_id,
            commodity,
            containers_count,
            container_type,
            container_size,
            cargo_weight_per_container,
        )
        data = jsonable_encoder(data)
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )
    

@haulage_freight_router.post("/create_haulage_freight_rate")
def create_haulage_freight_rate_func(request: CreateHaulageFreightRate, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        # request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        rate = create_haulage_freight_rate(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })


@haulage_freight_router.post("/update_haulage_freight_rate")
def update_haulage_freight_rate_func(request: UpdateHaulageFreightRate, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        # request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        rate = update_haulage_freight_rate(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(rate))
    except HTTPException as e:
        raise
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e), 'traceback': traceback.print_exc() })

@haulage_freight_router.get("/list_haulage_freight_rate_requests")
def list_haulage_freight_rate_requests_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    performed_by_id: str = None,
    is_stats_required: bool = True,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = list_haulage_freight_rate_requests(filters, page_limit, page, performed_by_id, is_stats_required)
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
    
@haulage_freight_router.post("/create_haulage_freight_rate_request")
def create_haualge_freight_rate_request_data(request: CreateHaulageFreightRateRequest, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = create_haulage_freight_rate_request(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
    
@haulage_freight_router.post("/delete_haulage_freight_rate_request")
def delete_fcl_freight_rates_request(request: DeleteHaulageFreightRateRequest, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        delete_rate = delete_haulage_freight_rate_request(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(delete_rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })





@haulage_freight_router.get("/list_haulage_freight_rate_requests")
def list_haulage_freight_rate_requests_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    performed_by_id: str = None,
    is_stats_required: bool = True,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = list_haulage_freight_rate_requests(filters, page_limit, page, performed_by_id, is_stats_required)
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
    
@haulage_freight_router.post("/create_haulage_freight_rate_request")
def create_haualge_freight_rate_request_data(request: CreateHaulageFreightRateRequest, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = create_haulage_freight_rate_request(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
    
@haulage_freight_router.post("/delete_haulage_freight_rate_request")
def delete_fcl_freight_rates_request(request: DeleteHaulageFreightRateRequest, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        delete_rate = delete_haulage_freight_rate_request(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(delete_rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

