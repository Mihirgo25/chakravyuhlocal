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