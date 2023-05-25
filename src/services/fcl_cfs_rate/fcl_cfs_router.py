from fastapi import APIRouter, Query, Depends
from fastapi.responses import JSONResponse
from typing import Union, List
import json
import traceback
from fastapi.encoders import jsonable_encoder
from params import *
from datetime import datetime, timedelta
from rms_utils.auth import authorize_token
import sentry_sdk
from fastapi import HTTPException
from services.fcl_cfs_rate.interaction.create_fcl_cfs_rate import create_fcl_cfs_rates
from services.fcl_cfs_rate.interaction.get_fcl_cfs_rate import get_fcl_cfs_rate
from services.fcl_cfs_rate.interaction.list_fcl_cfs_rate import list_fcl_cfs_rate
from services.fcl_cfs_rate.interaction.get_cfs_rate_card import get_fcl_cfs_rate_card

fcl_cfs_router = APIRouter()

@fcl_cfs_router.post('/create_fcl_cfs_rate')
def create_fcl_cfs_rate(request: CreateFclCfsRate, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = create_fcl_cfs_rates(request.dict(exclude_none=False))
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
                       country_id: str = None,
                       container_size: str,
                       container_type: str,
                       commodity: str = None,
                        importer_exporter_id: str,
                       containers_count: int, 
                       bls_count: int,
                       cargo_weight_per_container: int = None,
                       additional_services: List[str] = [],
                       cargo_value: int = None, 
                       cargo_value_currency: str = None,
                       include_confirmed_inventory_rates: bool = False,
                       resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)    
    try:
        data = get_fcl_cfs_rate_card(trade_type, cargo_handling_type, port_id, country_id,
                             container_size, container_type, commodity, importer_exporter_id,
                             containers_count, bls_count, cargo_weight_per_container,
                             additional_services, cargo_value, cargo_value_currency,
                             include_confirmed_inventory_rates)
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })


@fcl_cfs_router.get("/get_fcl_cfs_rates")
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
        data = jsonable_encoder(data)
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) }) 


@fcl_cfs_router.get("/list_fcl_cfs_rates")
def list_fcl_cfs_rates(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    sort_by: str = 'updated_at',
    sort_type: str = 'desc',
    return_query: bool = False,
    pagination_data_required:bool = True,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = list_fcl_cfs_rate(filters, page_limit, page, sort_by, sort_type, return_query,pagination_data_required)
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })  