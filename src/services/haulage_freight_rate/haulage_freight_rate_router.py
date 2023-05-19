from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from params import *
from rms_utils.auth import authorize_token
import sentry_sdk
from fastapi import HTTPException
from services.haulage_freight_rate.haulage_params import HaulageFreightRate
from services.fcl_freight_rate.interaction.create_fcl_freight_commodity_cluster import create_fcl_freight_commodity_cluster
from services.haulage_freight_rate.interactions.rate_calculator import haulage_rate_calculator

haulage_freight_router = APIRouter()

@haulage_freight_router.post("/get_haulage_freight_rate_calculator")
def get_haulage_freight_rate(
    request: HaulageFreightRate,
    resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = haulage_rate_calculator(request)
        data = jsonable_encoder(data)
        return JSONResponse(status_code=200, content = data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

