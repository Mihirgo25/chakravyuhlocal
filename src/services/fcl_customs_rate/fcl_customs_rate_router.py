from fcl_customs_params import *
from rms_utils.auth import authorize_token
from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import sentry_sdk
from fastapi import HTTPException

from services.fcl_customs_rate.interactions.create_fcl_customs_rate import create_fcl_customs_rate_data


fcl_customs_router = APIRouter()

@fcl_customs_router.post("/create_fcl_customs_rate")
def create_fcl_freight_rate_func(request: CreateFclCustomsRate, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]

    try:
        rate = create_fcl_customs_rate_data(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e), 'traceback': traceback.print_exc() })
