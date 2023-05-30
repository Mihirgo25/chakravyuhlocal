from fcl_customs_params import *
from rms_utils.auth import authorize_token
from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import sentry_sdk, traceback
from fastapi import HTTPException

from services.fcl_customs_rate.interaction.create_fcl_customs_rate import create_fcl_customs_rate_data
from services.fcl_customs_rate.interaction.create_fcl_customs_rate_bulk_operation import create_fcl_customs_rate_bulk_operation
from services.fcl_customs_rate.interaction.create_fcl_customs_rate_feedback import create_fcl_customs_rate_feedback
from services.fcl_customs_rate.interaction.create_fcl_customs_rate_request import create_fcl_customs_rate_request
from services.fcl_customs_rate.interaction.create_fcl_customs_rate_not_available import create_fcl_customs_rate_not_available
from services.fcl_customs_rate.interaction.get_fcl_customs_rate_addition_frequency import get_fcl_customs_rate_addition_frequency
from services.fcl_customs_rate.interaction.get_fcl_customs_rate_visibility import get_fcl_customs_rate_visibility
from services.fcl_customs_rate.interaction.get_fcl_customs_rate import get_fcl_customs_rate
from services.fcl_customs_rate.interaction.list_fcl_customs_rates import list_fcl_customs_rates
from services.fcl_customs_rate.interaction.list_fcl_customs_rate_requests import list_fcl_customs_rate_requests
from services.fcl_customs_rate.interaction.list_fcl_customs_rate_feedbacks import list_fcl_customs_rate_feedbacks

fcl_customs_router = APIRouter()

@fcl_customs_router.post("/create_fcl_customs_rate")
def create_fcl_customs_rate_func(request: CreateFclCustomsRate, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]

    try:
        rate = create_fcl_customs_rate_data(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e), 'traceback': traceback.print_exc() })

@fcl_customs_router.post("/create_fcl_customs_rate_bulk_operation")
def create_fcl_customs_rate_bulk_operation_data(request: CreateFclCustomsRateBulkOperation, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        rate = create_fcl_customs_rate_bulk_operation(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
    
@fcl_customs_router.post("/create_fcl_customs_rate_feedback")
def create_fcl_customs_rate_feedback_data(request: CreateFclCustomsRateFeedback, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        rate = create_fcl_customs_rate_feedback(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@fcl_customs_router.post("/create_fcl_customs_rate_request")
def create_fcl_customs_rate_request_data(request: CreateFclCustomsRateRequest, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        rate = create_fcl_customs_rate_request(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@fcl_customs_router.post("/create_fcl_customs_rate_not_available")
def create_fcl_customs_rate_not_available_data(request: CreateFclCustomsRateNotAvailable, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        rate = create_fcl_customs_rate_not_available(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
    
@fcl_customs_router.get("/get_fcl_customs_rate_addition_frequency")
def get_fcl_customs_rate_addition_frequency_data(
    group_by: str,
    filters: str = None,
    sort_type: str = 'desc',
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = get_fcl_customs_rate_addition_frequency(group_by, filters, sort_type)
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
    

@fcl_customs_router.get("/get_fcl_customs_rate_visibility")
def get_fcl_customs_rate_visibility_data(
    service_provider_id: str,
    location_id: str = None,
    rate_id: str = None,
    container_size: str = None,
    container_type: str = None,
    commodity: str = None,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    request = {
        'service_provider_id' : service_provider_id,
        'location_id': location_id,
        'rate_id': rate_id,
        'container_size': container_size,
        'container_type': container_type,
        'commodity': commodity
    }
    try:
        data = get_fcl_customs_rate_visibility(request)
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
    
@fcl_customs_router.get("/get_fcl_customs_rate")
def get_fcl_customs_rate_data(
    id: str = None,
    location_id: str = None,
    container_size: str = None,
    container_type: str = None,
    commodity: str = None,
    service_provider_id: str = None,
    importer_exporter_id: str = None,
    trade_type: str = None,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    request = {
        'id':id,
        'location_id':location_id,
        'container_size' : container_size,
        'container_type' : container_type,
        'commodity' : commodity,
        'service_provider_id': service_provider_id,
        'importer_exporter_id': importer_exporter_id,
        'trade_type': trade_type,
    }

    try:
        data = get_fcl_customs_rate(request)
        data = jsonable_encoder(data)
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
    

@fcl_customs_router.get("/list_fcl_customs_rate_feedbacks")
def list_fcl_customs_rate_feedbacks_data(
    filters: str = None,
    spot_search_details_required: bool = False,
    page_limit: int = 10,
    page: int = 1,
    performed_by_id: str = None,
    is_stats_required: bool = True,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        data = list_fcl_customs_rate_feedbacks(filters, spot_search_details_required, page_limit, page, performed_by_id, is_stats_required)
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
    
@fcl_customs_router.get("/list_fcl_customs_rate_requests")
def list_fcl_customs_rate_requests_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    performed_by_id: str = None,
    is_stats_required: bool = True,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = list_fcl_customs_rate_requests(filters, page_limit, page, performed_by_id, is_stats_required)
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
    
@fcl_customs_router.get("/list_fcl_customs_rates")
def list_fcl_customs_rates_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    sort_by: str = 'updated_at',
    sort_type: str = 'desc',
    pagination_data_required: bool = False,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = list_fcl_customs_rates(filters, page_limit, page, sort_by, sort_type, pagination_data_required)
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })