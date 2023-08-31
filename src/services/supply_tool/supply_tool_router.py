from fastapi import APIRouter, Query, Depends, Request
from fastapi.responses import JSONResponse
from typing import Union, List
import json
import traceback
from libs.json_encoder import json_encoder
from params import *
from datetime import datetime, timedelta
from rms_utils.auth import authorize_token
import sentry_sdk
from fastapi import HTTPException


from services.supply_tool.interactions.list_fcl_freight_cancelled_shipments import list_fcl_freight_cancelled_shipments

supply_tool_router = APIRouter()

@supply_tool_router.get("/list_fcl_freight_cancelled_shipments")
def list_fcl_freight_cancelled_shipments_api(
        service: str,
        user_id: str,
        origin_location_id: str = None,
        destination_location_id: str = None,
        shipping_line_id: str = None,
        commodity: str = None,
        resp: dict = Depends(authorize_token)
    ):
    if resp["status_code"] != 200:
        return JSONResponse(status_code = resp["status_code"], content = resp)
    params = {
        'service': service,
        'user_id': user_id,
        'origin_location_id': origin_location_id,
        'destination_location_id': destination_location_id,
        'shipping_line_id': shipping_line_id,
        'commodity': commodity
    }
    try:
        resp = list_fcl_freight_cancelled_shipments(params)
        return JSONResponse(status_code=200, content=json_encoder(resp))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })