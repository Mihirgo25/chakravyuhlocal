from fastapi import APIRouter, Depends, HTTPException
from rms_utils.auth import authorize_token
from fastapi.responses import JSONResponse
import sentry_sdk
from services.trailer_freight_rates.interaction.get_trailer_freight_rate_estimation import get_estimated_rate
from fastapi.encoders import jsonable_encoder

trailer_router = APIRouter()

@trailer_router.get("/get_estimated_trailer_freight_rate")
def get_trailer_freight_rate_estimate(
    origin_location_id: str = None,
    destination_location_id: str = None,
    container_size: str = None,
    container_type: str = None,
    containers_count: int =None,
    cargo_weight_per_container: float = None,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    
    request = {
        "origin_location_id": origin_location_id,
        "destination_location_id": destination_location_id,
        "container_size": container_size,
        "container_type": container_type,
        "containers_count": containers_count,
        "cargo_weight_per_container": cargo_weight_per_container
    }

    try:
        data = get_estimated_rate(request)
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
