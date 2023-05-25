from fastapi import APIRouter, Query, Depends,HTTPException
from rms_utils.auth import authorize_token
from fastapi.responses import JSONResponse
import json
from fastapi.encoders import jsonable_encoder
from air_freight_rate_params import *
import sentry_sdk


from services.air_freight_rate.interaction.delete_air_freight_rate import delete_air_freight_rate
from services.air_freight_rate.interaction.update_air_freight_rate import update_air_freight_rate
air_freight_router = APIRouter()

@air_freight_router.post("/create_air_freight_rate")
def create_air_freight_rate():
    return



@air_freight_router.post("/delete_air_freight_rate")
def delete_air_freight_rate(request: DeleteAirFreightRate, resp: dict = Depends(authorize_token)):
    if resp["status_code"]!=200:
        return JSONResponse(status_code=resp['status_code'],content=resp)
    if resp["isAuthoirized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        delete_rate=delete_air_freight_rate(request.dict(exclude_none=True))
        return JSONResponse(status_code=200,content=jsonable_encoder(delete_rate))
    except HTTPException as e :
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@air_freight_router.post("/update_air_freight_rate")
def update_air_freight_rate(request: UpdateAirFreightRate, resp:dict =Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = update_air_freight_rate(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })



