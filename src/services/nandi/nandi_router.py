from fastapi import HTTPException, APIRouter, Depends
from rms_utils.auth import authorize_token
import sentry_sdk
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from nandi_params import *
from services.nandi.interactions.create_draft_fcl_freight_rate import create_draft_fcl_freight_rate_data
from services.nandi.interactions.create_draft_fcl_freight_rate_local import create_draft_fcl_freight_rate_local_data
from services.nandi.interactions.update_draft_fcl_freight_rate import update_draft_fcl_freight_rate_data
from services.nandi.interactions.update_draft_fcl_freight_rate_local import update_draft_fcl_freight_rate_local_data
from services.nandi.interactions.list_draft_fcl_freight_rates import list_draft_fcl_freight_rates
from services.nandi.interactions.list_draft_fcl_freight_rate_locals import list_draft_fcl_freight_rate_locals
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_local import create_fcl_freight_rate_local
import copy

nandi_router = APIRouter()

@nandi_router.post("/create_draft_fcl_freight_rate")
def create_draft_fcl_freight_rate(request: CreateDraftFclFreightRate, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    draft_freight = create_draft_fcl_freight_rate_data(request.dict(exclude_none=True))
    return JSONResponse(status_code=200, content=jsonable_encoder(draft_freight))

@nandi_router.post("/create_draft_fcl_freight_rate_local")
def create_draft_fcl_freight_rate_local(request: CreateDraftFclFreightRateLocal, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    draft_freight_local = create_draft_fcl_freight_rate_local_data(request.dict(exclude_none=True))
    return JSONResponse(status_code=200, content=jsonable_encoder(draft_freight_local))

@nandi_router.post("/update_draft_fcl_freight_rate")
def update_draft_fcl_freight_rate(request: UpdateDraftFclFreightRate, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    draft_freight = update_draft_fcl_freight_rate_data(request.dict(exclude_none=True))
    return JSONResponse(status_code=200, content=jsonable_encoder(draft_freight))

@nandi_router.post("/update_draft_fcl_freight_rate_local")
def update_draft_fcl_freight_rate_local(request: UpdateDraftFclFreightRateLocal, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    draft_freight = update_draft_fcl_freight_rate_local_data(request.dict(exclude_none=True))
    return JSONResponse(status_code=200, content=jsonable_encoder(draft_freight))

@nandi_router.get("/list_draft_fcl_freight_rates")
def list_draft_fcl_freight_rate_data(
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
        data = list_draft_fcl_freight_rates(filters, page_limit, page, sort_by, sort_type)
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@nandi_router.get("/list_draft_fcl_freight_rate_locals")
def list_draft_fcl_freight_rate_locals_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    sort_by: str = 'updated_at',
    sort_type: str = 'desc',
    is_stats_required: bool = True,
    resp: dict = Depends(authorize_token)
    ):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = list_draft_fcl_freight_rate_locals(filters, page_limit, page, sort_by, sort_type, is_stats_required)
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@nandi_router.post("/create_fcl_freight_rate_local_for_draft")
def create_fcl_freight_rate_local_for_draft(request: CreateFclFreightDraftLocal, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]

    request = request.dict(exclude_none=False)
    params = copy.deepcopy(request)
    del params['source']

    fcl_freight_local = create_fcl_freight_rate_local(params)
    if 'id' in fcl_freight_local:
        request['rate_id'] = fcl_freight_local['id']
        draft_freight_local = create_draft_fcl_freight_rate_local_data(request)
    return JSONResponse(status_code=200, content=jsonable_encoder(draft_freight_local))