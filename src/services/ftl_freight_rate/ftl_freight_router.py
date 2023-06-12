from fastapi import APIRouter, Depends
from rms_utils.auth import authorize_token
from fastapi.responses import JSONResponse
import sentry_sdk
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException
from services.ftl_freight_rate.interactions.get_estimated_ftl_freight_rate import (
    get_ftl_freight_rate,
)
from services.ftl_freight_rate.interactions.list_ftl_freight_rule_sets import (
    list_ftl_rule_set_data,
)
from services.ftl_freight_rate.interactions.create_ftl_freight_rate_rule_set import (
    create_ftl_rule_set_data,
)
from services.ftl_freight_rate.interactions.update_ftl_freight_rate_rule_set import (
    update_ftl_rule_set_data,
)
from services.ftl_freight_rate.interaction.list_trucks import list_trucks_data
from services.ftl_freight_rate.interaction.create_truck import create_truck_data
from services.ftl_freight_rate.interaction.update_truck import update_truck_data
from services.ftl_freight_rate.ftl_params import *
from services.ftl_freight_rate.interaction.create_fuel_data import create_fuel_data

ftl_freight_router = APIRouter()


@ftl_freight_router.get("/get_estimated_ftl_freight_rate")
def get_ftl_freight_rates(
    origin_location_id: str = None,
    destination_location_id: str = None,
    trip_type: str = "one_way",
    truck_type: str = None,
    commodity: str = None,
    weight: str = None,
    truck_body_type: str = None,
    resp: dict = Depends(authorize_token),
):
    if resp['status_code'] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    if weight:
        weight = float(weight)
        
    data = get_ftl_freight_rate(
        origin_location_id,
        destination_location_id,
        commodity,
        weight,
        truck_type,
        truck_body_type,
        trip_type,
    )
    data = jsonable_encoder(data)
    return JSONResponse(status_code=200, content=data)

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

@ftl_freight_router.get("/list_ftl_freight_rate_rule_sets")
def list_ftl_rule_set(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    sort_by: str = "created_at",
    sort_type: str = "asc",
    pagination_data_required: bool = False,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = list_ftl_rule_set_data(
            filters, page_limit, page, sort_by, sort_type, pagination_data_required
        )
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@ftl_freight_router.post("/create_ftl_freight_rate_rule_set")
def create_ftl_rule_set(
    request: CreateFtlRuleSet, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
    try:
        data = create_ftl_rule_set_data(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@ftl_freight_router.post("/update_ftl_freight_rate_rule_set")
def update_ftl_rule_set(
    request: UpdateFtlRuleSet, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = update_ftl_rule_set_data(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )

@ftl_freight_router.get("/list_trucks")
def list_trucks(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    sort_by: str = 'created_at',
    sort_type: str = 'asc',
    pagination_data_required: bool = True,
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
    try:
        data = create_truck_data(request.dict())
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@ftl_freight_router.post("/update_truck")
def update_truck(request: UpdateTruck, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = update_truck_data(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
