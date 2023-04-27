from fastapi import APIRouter, Query, Depends
from rms_utils.auth import authorize_token
from fastapi.responses import JSONResponse
import sentry_sdk
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException

from services.ftl_freight_rate.interaction.list_trucks import list_trucks_data
from services.ftl_freight_rate.interaction.create_truck import create_truck_data
from services.ftl_freight_rate.interaction.update_truck import update_truck_data

from services.ftl_freight_rate.ftl_params import *

ftl_freight_router = APIRouter()

@ftl_freight_router.get("/list_trucks")
def list_trucks(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    sort_by: str = 'created_at',
    sort_type: str = 'asc',
    pagination_data_required: bool = False,
    resp: dict = Depends(authorize_token)
):
        if resp["status_code"] != 200:
            return JSONResponse(status_code=resp["status_code"], content=resp)
        try:
            data = list_trucks_data(filters, page_limit, page, sort_by, sort_type, pagination_data_required)
            return JSONResponse(status_code=200, content=data)
        except HTTPException as e:
            raise
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@ftl_freight_router.post("/create_truck")
def create_truck(request: CreateTruck, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = create_truck_data(request.dict(exclude_none=False))
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@ftl_freight_router.post("/update_truck")
def create_truck(request: UpdateTruck, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = update_truck_data(request.dict(exclude_none=False))
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })