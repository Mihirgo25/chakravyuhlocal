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
from services.air_freight_rate.interaction.list_air_freight_rate_surcharges import list_air_freight_rate_surcharges
from services.air_freight_rate.interaction.get_air_freight_rate_surcharge import get_air_freight_rate_surcharge
from services.air_freight_rate.interaction.create_air_freight_rate_surcharge import create_air_freight_rate_surcharge
from services.air_freight_rate.interaction.create_air_freight_rate_local import create_air_freight_rate_local
from services.air_freight_rate.interaction.update_air_freight_rate_surcharge import update_air_freight_rate_surcharge
from services.air_freight_rate.interaction.create_air_freight_rate_task import create_air_freight_rate_task
from services.air_freight_rate.interaction.get_air_freight_rate_local import get_air_freight_rate_local
from services.air_freight_rate.interaction.update_air_freight_rate_local import update_air_freight_rate_local
from services.air_freight_rate.interaction.list_air_freight_rate_local import list_air_freight_rate_locals
from services.air_freight_rate.interaction.update_air_freight_rate_task import update_air_freight_rate_task_data
from services.air_freight_rate.interaction.update_air_freight_rate_local import update_air_freight_rate_local
from services.air_freight_rate.interaction.create_air_freight_rate_request import create_air_freight_rate_request


air_freight_router = APIRouter()


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


@air_freight_router.get("/get_air_freight_rate")
def get_air_freight_rate_data(
    origin_airport_id:str=None,
    destination_airport_id:str=None,
    commodity:str=None,
    commodity_type:str=None,
    commodity_sub_type:str =None,
    airline_id:str=None,
    operation_type:str=None,
    service_provider_id:str=None,
    shipment_type:str ='box',
    stacking_type:str = 'stackable',
    validity_start:datetime =datetime.now(),
    validity_end:datetime =datetime.now(),
    weight:float =None,
    cargo_readiness_date:datetime=datetime.now(),
    price_type:str=None,
    cogo_entity_id:str=None,
    trade_type:str=None,
    volume:float =None,
    predicted_rates_required:bool=False,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    request = {
        'id':id,
        'origin_airport_id':origin_airport_id,
        'destination_airport_id':destination_airport_id,
        'commodity' : commodity,
        'commodity_type':commodity_type,
        'commodity_sub_type' : commodity_sub_type,
        'airline_id':airline_id,
        'operation_type':operation_type,
        'shipment_type' : shipment_type,
        'service_provider_id': service_provider_id,
        'stacking_type': stacking_type,
        'cogo_entity_id': cogo_entity_id,
        'validity_start':validity_start,
        'validity_end':validity_end,
        'weight':weight,
        'cargo_readiness_date':cargo_readiness_date,
        'price_type':price_type,
        'trade_type':trade_type,
        'volume':volume,
        'predicted_rates_required':predicted_rates_required
    }

    try:
        data = get_air_freight_rate(request)
        data = jsonable_encoder(data)
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        # sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
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
    
    try:
        data = update_air_freight_rate_local(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@air_freight_router.post("/create_air_freight_rate_local")
def create_air_freight_rate_local_data(request: CreateAirFreightRateLocal, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]

    try:
        data = create_air_freight_rate_local(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@air_freight_router.post("/create_air_freight_rate_surcharge")
def create_air_freight_rate_surcharge_data(request: CreateAirFreightRateSurcharge, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]

    try:
        data = create_air_freight_rate_surcharge(request.dict(exclude_none=True))
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

@air_freight_router.post("/update_air_freight_rate_surcharge")
def update_air_freight_rate_surcharge_data(request: UpdateAirFreightRateSurcharge, resp:dict = Depends(authorize_token)):
   
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        
    try:
        data = update_air_freight_rate_surcharge(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@air_freight_router.get("/get_air_freight_rate_surcharge")
def get_air_freight_rate_surcharge_data(
    origin_airport_id: str=None,
    destination_airport_id: str=None,
    commodity: str=None,
    airline_id: str=None,
    operation_type: str=None,
    service_provider_id: str=None,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    request={
        'origin_airport_id':origin_airport_id,
        'destination_airport_id':destination_airport_id,
        'commodity':commodity,
        'airline_id':airline_id,
        'operation_type':operation_type,
        'service_provider_id':service_provider_id,
    }

    try:
        data = get_air_freight_rate_surcharge(request)
        data = jsonable_encoder(data)
        return JSONResponse(status_code=200, content = data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
    
    

@air_freight_router.post("/create_air_freight_rate_tasks")
def create_air_freight_rate_task_data(request: CreateAirFreightRateTask, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = create_air_freight_rate_task(request.dict(exclude_none = False))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

        
@air_freight_router.get("/list_air_freight_rate_surcharges")
def list_air_freight_rate_surcharges_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    pagination_data_required: bool = True,
    return_query: bool = True,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        data = list_air_freight_rate_surcharges(filters, page_limit, page, pagination_data_required,return_query)
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        # sentry_sdk.capture_exception(e)
        print(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@air_freight_router.post("/update_air_freight_rate_task")
def update_air_freight_rate_task(request:UpdateAirFreightRateTask  , resp:dict = Depends(authorize_token)):
    if resp['status_code']!=200:
        return JSONResponse(status_code=resp['status_code'],content=resp)
    try:
        return JSONResponse(status_code=200, content=update_air_freight_rate_task_data(request.dict(exclude_none=False)))
    except HTTPException as e:
        raise
    except Exception as e:
        # sentry_sdk.capture_exception(e)
        print(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@air_freight_router.post('/create_air_freight_rate_request')
def create_air_freight_rate_request_data(request:CreateAirFreightRateRequest,resp:dict=Depends(authorize_token)):
    if resp['status_code']!=200:
        return JSONResponse(status_code=resp['status_code'],content=resp)
    # try:
    return JSONResponse(status_code=200,content=create_air_freight_rate_request(request.dict(exclude_none=False)))
    # except HTTPException as h :
    #     raise
    # except Exception as e:
    #     print(e)
    #     return JSONResponse(status_code=500,content={"success":False,'error':str(e)})