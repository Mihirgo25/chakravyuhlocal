from fastapi import APIRouter, Query, Depends
from rms_utils.auth import authorize_token
from fastapi.responses import JSONResponse
import sentry_sdk
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException
from services.ftl_freight_rate.interaction.create_fuel_data import create_fuel_data

from services.ftl_freight_rate.ftl_params import *

ftl_freight_router = APIRouter()
    
@ftl_freight_router.post("/create_fuel_data")
def create_fuel_datas(request: CreateFuelData,resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = create_fuel_data(request.dict(exclude_none=False))
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })