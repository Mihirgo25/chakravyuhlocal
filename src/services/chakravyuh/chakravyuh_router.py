from chakravyuh_params import *
from rms_utils.auth import authorize_token
from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import sentry_sdk
from fastapi import HTTPException

from services.chakravyuh.interaction.create_fcl_freight_rate_estimation import create_fcl_freight_rate_estimation
from services.chakravyuh.interaction.create_fcl_freight_rate_local_estimation import create_fcl_freight_rate_local_estimation
from services.chakravyuh.migrated_estimated_local_rates import migrate_estimated_local_rates
from services.chakravyuh.interaction.create_demand_transformation import create_demand_transformation
from services.chakravyuh.interaction.create_revenue_target import create_revenue_target

# get apis
from services.chakravyuh.interaction.get_periodic_fcl_freight_rate_estimation_trends import get_periodic_fcl_freight_rate_estimation_trends
from services.chakravyuh.interaction.list_fcl_freight_rate_estimation_trends import list_fcl_freight_rate_estimation_trends
from services.chakravyuh.interaction.list_fcl_freight_rate_estimations import list_fcl_freight_rate_estimations

chakravyuh_router = APIRouter()

@chakravyuh_router.post("/create_fcl_estimated_rate")
def create_fcl_estimated_rates(request: PostFclEstimatedRate, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    estimated_rate = create_fcl_freight_rate_estimation(request.dict(exclude_none=True))
    return JSONResponse(status_code=200, content=jsonable_encoder(estimated_rate))

@chakravyuh_router.post("/create_fcl_local_estimated_rate")
def create_fcl_local_estimated_rates(request: PostFclLocalEstimatedRate, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    estimated_local_rate = create_fcl_freight_rate_local_estimation(request.dict(exclude_none=True))
    return JSONResponse(status_code=200, content=jsonable_encoder(estimated_local_rate))

@chakravyuh_router.post("/create_demand_transformation")
def create_demand_transformation_func(request: PostDemandTransformation, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    demand = create_demand_transformation(request.dict(exclude_none=True))
    return JSONResponse(status_code=200, content=jsonable_encoder(demand))

@chakravyuh_router.post("/create_revenue_target")
def create_revenue_target_func(request: PostRevenueTarget, resp:dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    target = create_revenue_target(request.dict(exclude_none=True))
    return JSONResponse(status_code=200, content=jsonable_encoder(target))

@chakravyuh_router.get('/list_fcl_freight_rate_estimations')
def list_fcl_freight_rate_estimations_api(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    sort_by: str = 'updated_at',
    sort_type: str = 'desc',
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = list_fcl_freight_rate_estimations(filters, page_limit, page, sort_by, sort_type)
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@chakravyuh_router.get('/list_fcl_freight_rate_estimation_trends')
def list_fcl_freight_rate_estimation_trends_api(
    filters: str = None,
    page_limit: int = 20,
    page: int = 1,
    sort_by: str = 'created_at',
    sort_type: str = 'desc',
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = list_fcl_freight_rate_estimation_trends(filters, page_limit, page, sort_by, sort_type)
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@chakravyuh_router.get('/get_periodic_fcl_freight_rate_estimation_trends')
def list_fcl_freight_rate_estimation_trends_api(
    estimation_id: int,
    created_at_greater_than: datetime = datetime.now() - timedelta(days=7),
    created_at_less_than: datetime = datetime.now(),
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = get_periodic_fcl_freight_rate_estimation_trends(estimation_id, created_at_greater_than, created_at_less_than)
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

    
@chakravyuh_router.post("/migrate_locals")
def migration_locals():
    migrate_estimated_local_rates()


