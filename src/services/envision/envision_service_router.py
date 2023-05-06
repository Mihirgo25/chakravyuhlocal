from fastapi import APIRouter, Depends, HTTPException
from rms_utils.auth import authorize_token
from fastapi.responses import JSONResponse
import sentry_sdk
from services.envision.envision_params import *
from services.envision.interaction.get_ftl_freight_predicted_rate import predict_ftl_freight_rate
from services.envision.interaction.create_ftl_freight_rate_prediction_feedback import (
    create_ftl_freight_rate_feedback
)
from services.envision.interaction.create_air_freight_rate_prediction_feedback import create_air_freight_rate_feedback
from services.envision.interaction.get_air_freight_predicted_rate import predict_air_freight_rate
from services.envision.interaction.get_haulage_freight_predicted_rate import predict_haulage_freight_rate
from services.envision.interaction.create_haulage_freight_rate_prediction_feedback import (
    create_haulage_freight_rate_feedback
)
from fastapi.encoders import jsonable_encoder

envision_router = APIRouter()

@envision_router.post("/get_ftl_freight_predicted_rate")
def get_ftl_freight_predicted_rate(request: FtlFreightRate, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    result = []
    try:
        for param in request.params:
            try:
                param = predict_ftl_freight_rate(param)
            except:
                param = param.__dict__
                param["predicted_price"] = None
        result.append(param)
        data = create_ftl_freight_rate_feedback(result)
        if data:
            return JSONResponse(status_code = 200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@envision_router.post("/get_haulage_freight_predicted_rate")
def get_haulage_freight_predicted_rate(request: HaulageFreightRate, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    result = []
    try:
        for param in request.params:
            try:
                param = predict_haulage_freight_rate(param)
            except:
                param = param.__dict__
                param["predicted_price"] = None
        result.append(param)
        data = create_haulage_freight_rate_feedback(result)
        if data:
            return JSONResponse(status_code = 200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@envision_router.post("/get_air_freight_predicted_rate")
def get_air_freight_predicted_rate(request: AirFreightRate, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    result = []
    try:
        for param in request.params:
            try:
                param = predict_air_freight_rate(param)
            except:
                param = param.__dict__
                param["predicted_price"] = None
        result.append(param)
        data = create_air_freight_rate_feedback(result)
        if data:
            return JSONResponse(status_code = 200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
