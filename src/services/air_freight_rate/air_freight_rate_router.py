from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
import sentry_sdk
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from rms_utils.auth import authorize_token
from services.air_freight_rate.air_freight_rate_params import CreateDraftAirFreightRateParams

from services.air_freight_rate.interactions.create_draft_air_freight_rate import create_draft_air_freight_rate

extension_router = APIRouter()

@extension_router.post("/create_draft_air_freight_rate")
def create_draft_air_freight_rate_api(request: CreateDraftAirFreightRateParams, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = create_draft_air_freight_rate(request.dict(exclude_none=False))
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })