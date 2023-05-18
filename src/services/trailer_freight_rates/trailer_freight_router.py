from fastapi import APIRouter, Depends, HTTPException
from rms_utils.auth import authorize_token
from fastapi.responses import JSONResponse
import sentry_sdk
from services.trailer_freight_rates.interaction.create_trailer_freight_rate_constant import create_trailer_constant_data
from services.trailer_freight_rates.trailer_params import *
from fastapi.encoders import jsonable_encoder
from services.trailer_freight_rates.interaction.trailer_freight_rate_calculate import calculate_trailer_rate

trailer_router = APIRouter()

@trailer_router.post("/create_trailer_freight_constant")
def create_trailer_freight_constant(request: TrailerConstants, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = create_trailer_constant_data(request.dict(exclude_none=False))
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@trailer_router.post("/calculate_trailer_freight_rate")
def calculate_trailer_freight_rate(request: TrailerRateCalculator, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = calculate_trailer_rate(request.dict(exclude_none=False))
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })