from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from libs.json_encoder import json_encoder
from params import *
from rms_utils.auth import authorize_token
import sentry_sdk
from fastapi import HTTPException
from services.haulage_freight_rate.interactions.get_estimated_haulage_freight_rate import (
    haulage_rate_calculator,
)

haulage_freight_router = APIRouter()


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
        data = json_encoder(data)
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )
