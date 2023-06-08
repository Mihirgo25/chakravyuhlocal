from fastapi import APIRouter, Query, Depends
from fastapi.responses import JSONResponse
from typing import List
from fastapi.encoders import jsonable_encoder
from fcl_cfs_params import *
from rms_utils.auth import authorize_token
import sentry_sdk
from fastapi import HTTPException
from services.fcl_cfs_rate.interaction.create_fcl_cfs_rate import create_fcl_cfs_rates
from services.fcl_cfs_rate.interaction.get_fcl_cfs_rate import get_fcl_cfs_rate
from services.fcl_cfs_rate.interaction.list_fcl_cfs_rate import list_fcl_cfs_rate
from services.fcl_cfs_rate.interaction.get_cfs_rate_cards import get_fcl_cfs_rate_cards
from services.fcl_cfs_rate.interaction.list_fcl_cfs_rate_request import list_fcl_cfs_rate_request
from services.fcl_cfs_rate.interaction.create_fcl_cfs_rate_request import create_fcl_cfs_rate_request
from services.fcl_cfs_rate.interaction.create_fcl_cfs_rate_not_available import create_fcl_cfs_rate_not_available
from services.fcl_cfs_rate.interaction.delete_fcl_cfs_rate import delete_fcl_cfs_rate
from services.fcl_cfs_rate.interaction.delete_fcl_cfs_rate_request import delete_fcl_cfs_rate_request
from services.fcl_cfs_rate.interaction.update_fcl_cfs_rate import update_fcl_cfs_rate
from services.fcl_cfs_rate.interaction.create_fcl_cfs_rate_bulk_operation import create_fcl_cfs_rate_bulk_operation
from services.fcl_cfs_rate.interaction.update_fcl_cfs_rate_platform_prices import update_fcl_cfs_rate_platform_prices
fcl_cfs_router = APIRouter()

@fcl_cfs_router.post('/create_fcl_cfs_rate')
def create_fcl_cfs_rate(request: CreateFclCfsRate, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
    try:
        data = create_fcl_cfs_rates(request.dict(exclude_none=False))
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
    

@fcl_cfs_router.post('/create_fcl_cfs_rate_request')
def create_fcl_cfs_rate_requests(request: FclCfsRateRequest, resp: dict = Depends(authorize_token)): #
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = create_fcl_cfs_rate_request(request.dict(exclude_none=False))
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
    
@fcl_cfs_router.post('/create_fcl_cfs_rate_not_available')
def create_fcl_cfs_rate_not_available_data(request: CreateFclCfsRateNotAvailable, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = create_fcl_cfs_rate_not_available(request.dict(exclude_none=False))
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })


@fcl_cfs_router.post('/create_fcl_cfs_rate_bulk_operation')
def create_fcl_customs_rate_bulk_operation_data(request: CreateFclCfsRateBulkOperation, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = create_fcl_cfs_rate_bulk_operation(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })


@fcl_cfs_router.post('/update_fcl_cfs_rate')
def update_fcl_cfs_rates(request: UpdateFclCfsRate, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = update_fcl_cfs_rate(request.dict(exclude_none=False))
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })


@fcl_cfs_router.get("/get_fcl_cfs_rate_cards")
def get_cfs_rate_cards(trade_type: str,
                       cargo_handling_type: str,
                       port_id: str,
                       container_size: str,
                       container_type: str,
                       containers_count: int, 
                       bls_count: int,
                       importer_exporter_id: str = None,
                       country_id: str = None,
                       commodity: str = None,
                       cargo_weight_per_container: int = None,
                       additional_services: List[str] | None= Query(None),
                       cargo_value: int = None, 
                       cargo_value_currency: str = None,
                       include_confirmed_inventory_rates: bool = False,
                       resp: dict = Depends(authorize_token)):
    
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)    
    try:
        request = {
            'trade_type':trade_type,
            'cargo_handling_type': cargo_handling_type,
            'port_id':port_id,
            'country_id':country_id,
            'container_size':container_size,
            'container_type':container_type,
            'commodity':commodity,
            'importer_exporter_id':importer_exporter_id,
            'containers_count':containers_count,
            'bls_count':bls_count,
            'cargo_weight_per_container':cargo_weight_per_container,
            'additional_services':additional_services,
            'cargo_value':cargo_value,
            'cargo_value_currency':cargo_value_currency,
            'include_confirmed_inventory_rates':include_confirmed_inventory_rates
        }
        data = get_fcl_cfs_rate_cards(request)
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })


@fcl_cfs_router.get("/get_fcl_cfs_rate")
def get_fcl_cfs_rates(location_id: str = None,
                    trade_type: str = None,
                    container_size: str = None,
                    container_type: str = None,
                    commodity: str = None,
                    service_provider_id: str = None,
                    importer_exporter_id: str = None,
                    cargo_handling_type: str = None,
                    resp: dict = Depends(authorize_token)
                    ):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    request = {
        'location_id': location_id,
        'trade_type': trade_type,
        'container_size': container_size,
        'container_type': container_type,
        'commodity': commodity,
        'service_provider_id': service_provider_id,
        'importer_exporter_id': importer_exporter_id,
        'cargo_handling_type': cargo_handling_type
    }
    try:
        data = get_fcl_cfs_rate(request)
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) }) 


@fcl_cfs_router.get("/list_fcl_cfs_rates")
def list_fcl_cfs_rates_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    sort_by: str = 'updated_at',
    sort_type: str = 'desc',
    return_query: bool = False,
    pagination_data_required: bool = False,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = list_fcl_cfs_rate(filters, page_limit, page, sort_by, sort_type,pagination_data_required, return_query)
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) }) 

@fcl_cfs_router.get("/list_fcl_cfs_rate_requests") 
def list_fcl_cfs_rate_requests(
    filters: str = {},
    page_limit: int = 10,
    page: int = 1,
    is_stats_required: bool = True,
    performed_by_id: str = None,
    resp: dict  = Depends(authorize_token)
    ):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = list_fcl_cfs_rate_request(filters, page_limit, page, is_stats_required, performed_by_id)
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@fcl_cfs_router.post("/delete_fcl_cfs_rate")
def delete_fcl_cfs_rates(request: DeleteFclCfsRate, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        delete_rate = delete_fcl_cfs_rate(request.dict(exclude_none=False))
        return JSONResponse(status_code=200, content=jsonable_encoder(delete_rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@fcl_cfs_router.post("/delete_fcl_cfs_rate_request")
def delete_fcl_cfs_rates_requests(request: DeleteFclCfsRateRequest, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        delete_rate = delete_fcl_cfs_rate_request(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(delete_rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@fcl_cfs_router.post("/update_fcl_cfs_platform_prices")
def update_fcl_cfs_platform_price(request:UpdateFclCfsRatePlatformPrice, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = update_fcl_cfs_rate_platform_prices(request.dict(exclude_none=False))
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
                                  