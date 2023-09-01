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
from services.supply_tool.interactions.list_fcl_freight_rate_coverages import list_fcl_freight_rate_coverages
from services.supply_tool.interactions.delete_fcl_freight_rate_job import delete_fcl_freight_rate_job
from services.supply_tool.supply_tool_params import DeleteFclFreightRateJob


supply_tool_router = APIRouter()

    
@supply_tool_router.post("/delete_fcl_freight_rate_job")
def delete_fcl_freight_rate_job_api(
    request: DeleteFclFreightRateJob, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
    try:
        rate = delete_fcl_freight_rate_job(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(rate))
    except HTTPException as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )