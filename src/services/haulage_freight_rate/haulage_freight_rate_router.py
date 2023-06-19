from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from params import *
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
from typing import List,Union

haulage_freight_router = APIRouter()
from services.haulage_freight_rate.interactions.create_haulage_freight_rate import create_haulage_freight_rate
from params import PostHaulageFreightRate

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
def create_haulage_freight_rate_func(request: PostHaulageFreightRate, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        rate = create_haulage_freight_rate(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(rate))
    except HTTPException as e:
        raise
    except Exception as e:
        # raise
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e)})
