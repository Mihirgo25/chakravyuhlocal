from fastapi import HTTPException, APIRouter, Depends
from rms_utils.auth import authorize_token
import sentry_sdk
from libs.json_encoder import json_encoder
from fastapi.responses import JSONResponse
from nandi_params import *
from services.nandi.interactions.create_draft_fcl_freight_rate import create_draft_fcl_freight_rate_data
from services.nandi.interactions.create_draft_fcl_freight_rate_local import create_draft_fcl_freight_rate_local_data
from services.nandi.interactions.update_draft_fcl_freight_rate import update_draft_fcl_freight_rate_data
from services.nandi.interactions.update_draft_fcl_freight_rate_local import update_draft_fcl_freight_rate_local_data
from services.nandi.interactions.list_draft_fcl_freight_rates import list_draft_fcl_freight_rates
from services.nandi.interactions.list_draft_fcl_freight_rate_locals import list_draft_fcl_freight_rate_locals
from services.fcl_freight_rate.interaction.create_fcl_freight_rate import create_fcl_freight_rate_data
from services.fcl_freight_rate.interaction.get_fcl_freight_rate import get_fcl_freight_rate
from services.nandi.helpers.check_fcl_freight_local_for_draft import check_fcl_freight_rate_local_for_draft
from services.nandi.interactions.validate_dislike_rates import validate_rate_feedback
nandi_router = APIRouter()

@nandi_router.post("/update_draft_fcl_freight_rate")
def update_draft_fcl_freight_rate(request: UpdateDraftFclFreightRate, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        draft_freight = update_draft_fcl_freight_rate_data(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(draft_freight))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@nandi_router.post("/update_draft_fcl_freight_rate_local")
def update_draft_fcl_freight_rate_local(request: UpdateDraftFclFreightRateLocal, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        draft_freight_local = update_draft_fcl_freight_rate_local_data(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(draft_freight_local))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

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
    is_stats_required: bool = False,
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
    try:
        request = request.dict(exclude_none=False)
        response = check_fcl_freight_rate_local_for_draft(request)
        return JSONResponse(status_code=200, content=json_encoder(response))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@nandi_router.post("/create_fcl_freight_rate_for_draft")
def create_fcl_freight_rate_for_draft(request: CreateFclFreightDraft, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        request = request.dict(exclude_none=False)
        get_fcl_params = {
            'origin_port_id': request.get('origin_port_id'),
            'origin_main_port_id': request.get('origin_main_port_id'),
            'destination_port_id': request.get('destination_port_id'),
            'destination_main_port_id': request.get('destination_main_port_id'),
            'container_size': request.get('container_size'),
            'container_type': request.get('container_type'),
            'commodity': request.get('commodity'),
            'shipping_line_id': request.get('shipping_line_id'),
            'service_provider_id': request.get('service_provider_id'),
            'importer_exporter_id': request.get('importer_exporter_id'),
            'rate_type': request.get('rate_type')
        }
        fcl_freight = get_fcl_freight_rate(get_fcl_params)

        if 'freight' not in fcl_freight:
            fcl_freight = create_fcl_freight_rate_data(request)
            request['rate_id'] = fcl_freight.get('id')
        else:
            request['rate_id'] = fcl_freight['freight'].get('id')

        draft_fcl_freight = create_draft_fcl_freight_rate_data(request)
        return JSONResponse(status_code=200, content=json_encoder(draft_fcl_freight))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
    
@nandi_router.get("/validate_rate_feedback")
def validate_rate_feedback_api(
    service_type: str,
    rate_id: str,
    feedbacks: list[str] = [],
    chargeable_weight: float = None,
    price: float = None,
    currency: str = None,
    resp: dict = Depends(authorize_token)
    ):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        request = {
            "service_type": service_type,
            "rate_id": rate_id,
            "feedbacks": feedbacks,
            "chargeable_weight": chargeable_weight,
            "price": price,
            "currency": currency,
        }
        object = validate_rate_feedback(request)
        return JSONResponse(status_code=200, content=json_encoder(object))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })