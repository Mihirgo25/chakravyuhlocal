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

from services.supply_tool.interactions.get_fcl_freight_rate_coverage_stats import get_fcl_freight_rate_coverage_stats

supply_tool_router = APIRouter()

@supply_tool_router.get("/get_fcl_freight_rate_coverage_stats")
def get_fcl_freight_rate_coverage_stats_api(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    sort_by: str = 'created_at',
    sort_type: str = 'desc',
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        data = get_fcl_freight_rate_coverage_stats(filters, page_limit, page, sort_by, sort_type)
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
