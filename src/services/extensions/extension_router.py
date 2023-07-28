from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
import sentry_sdk
from fastapi import HTTPException
from libs.json_encoder import json_encoder
from rms_utils.auth import authorize_token
from services.extensions.extension_params import *

from services.extensions.interactions.create_freight_look_rates import create_freight_look_rates
from services.extensions.interactions.create_new_max_rates import create_new_max_rates
from services.extensions.interactions.create_web_cargo_rates import create_web_cargo_rates
from services.extensions.interactions.create_freight_look_surcharge_rates import create_freight_look_surcharge_rate
extension_router = APIRouter()

@extension_router.post("/create_freight_look_rates")
def create_freight_look_rates_api(request: CreateFreightLookRatesParams):
    # if resp["status_code"] != 200:
    #     return JSONResponse(status_code=resp["status_code"], content=resp)
    # if resp["isAuthorized"]:
    #     request.performed_by_id = resp["setters"]["performed_by_id"]
    #     request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = create_freight_look_rates(request.dict(exclude_none=False))
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@extension_router.post("/create_new_max_rates")
def create_new_max_rates_api(request: CreateNewMaxRatesParams):
    # if resp["status_code"] != 200:
    #     return JSONResponse(status_code=resp["status_code"], content=resp)
    # if resp["isAuthorized"]:
    #     request.performed_by_id = resp["setters"]["performed_by_id"]
    #     request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = create_new_max_rates(request.dict(exclude_none=False))
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@extension_router.post("/create_web_cargo_rates")
def create_web_cargo_rates_api(request: CreateWebCargoRatesParams):
    # if resp["status_code"] != 200:
    #     return JSONResponse(status_code=resp["status_code"], content=resp)
    # if resp["isAuthorized"]:
    #     request.performed_by_id = resp["setters"]["performed_by_id"]
    #     request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = create_web_cargo_rates(request.dict(exclude_none=False))
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
    
@extension_router.post("/create_freight_look_surcharge_rates")
def create_freight_look_surcharge_rate_api(request: CreateFreightLookSurchargeParams):
    # if resp["status_code"] != 200:
    #     return JSONResponse(status_code=resp["status_code"], content=resp)
    # if resp["isAuthorized"]:
    #     request.performed_by_id = resp["setters"]["performed_by_id"]
    #     request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = create_freight_look_surcharge_rate(request.dict(exclude_none=False))
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })