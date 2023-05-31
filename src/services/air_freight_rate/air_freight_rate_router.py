from fastapi import APIRouter, Query, Depends,HTTPException
from rms_utils.auth import authorize_token
from fastapi.responses import JSONResponse
import json
from fastapi.encoders import jsonable_encoder
from air_freight_rate_params import *
import sentry_sdk
from fastapi.responses import JSONResponse
from typing import Union,List
import json
import traceback
from fastapi.encoders import jsonable_encoder
from params import *
from datetime import datetime,timedelta
from rms_utils.auth import authorize_token
import sentry_sdk
from fastapi import HTTPException

from services.air_freight_rate.interaction.delete_air_freight_rate import delete_air_freight_rate
from services.air_freight_rate.interaction.update_air_freight_rate import update_air_freight_rate
from services.air_freight_rate.interaction.get_air_freight_rate import get_air_freight_rate
air_freight_router = APIRouter()
from services.air_freight_rate.interaction.get_air_freight_rate_local import get_air_freight_rate_local
from services.air_freight_rate.interaction.update_air_freight_rate_local import update_air_freight_rate_local
from services.air_freight_rate.interaction.list_air_freight_rate_local import list_air_freight_rate_locals
@air_freight_router.post("/create_air_freight_rate")
def create_air_freight_rate():
    return



@air_freight_router.post("/delete_air_freight_rate")
def delete_air_freight_rates(request: DeleteAirFreightRate, resp: dict = Depends(authorize_token)):
    if resp["status_code"]!=200:
        return JSONResponse(status_code=resp['status_code'],content=resp)
    if resp["isAuthorized"]:
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
def update_air_freight_rates(request: UpdateAirFreightRate, resp:dict =Depends(authorize_token)):
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


@air_freight_router.get('/get_air_freught_router')
def get_air_freight_rate(request:GetAirFreightRate , resp:dict =Depends(authorize_token)):
    return
@air_freight_router.get("/get_air_freight_rate_local")
def get_air_freight_rate_local_data(
    airport_id:str=None,
    airline_id:str=None,
    trade_type:str=None,
    commodity:str=None,
    service_provider_id:str=None,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    request={
        'airport_id':airport_id,
        'airline_id':airline_id,
        'trade_type':trade_type,
        'commodity':commodity,
        'service_provider_id':service_provider_id,
    }

    try:
        data = get_air_freight_rate_local(request)
        data = jsonable_encoder(data)
        return JSONResponse(status_code=200, content = data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@air_freight_router.post("/update_air_freight_rate_local")
def update_air_freight_rates_locals(request: UpdateFrieghtRateLocal, resp:dict =Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    # if resp["isAuthorized"]:
    #     request.performed_by_id = resp["setters"]["performed_by_id"]
    #     request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = update_air_freight_rate_local(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
    
@air_freight_router.get("/list_air_freight_rate_locals")
def list_air_freight_rate_locals_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    sort_by: str = 'updated_at',
    sort_type: str = 'desc',
    return_query: bool = False,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = list_air_freight_rate_locals(filters, page_limit, page, sort_by, sort_type, return_query)
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })