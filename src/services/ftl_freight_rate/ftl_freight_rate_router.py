from fastapi import APIRouter, Query, Depends
from rms_utils.auth import authorize_token
from fastapi.responses import JSONResponse
import sentry_sdk
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException
from services.ftl_freight_rate.interactions.get_ftl_freight_rate import get_ftl_freight_rate
ftl_freight_router = APIRouter()

@ftl_freight_router.post('/get_ftl_freight_rate')
def get_ftl_freight_rates(
    origin_location_id: str = None,
    destination_location_id:str = None,
    commodity_type: str = None,
    truck_type: str =  None,
    truck_body_type: str = None,
    commodity_weight:float = None,
    resp:dict = Depends(authorize_token)):
    if resp['status_code'] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    data = get_ftl_freight_rate(origin_location_id,destination_location_id,commodity_type,truck_body_type,truck_body_type,commodity_weight)
    data = jsonable_encoder(data)
    return JSONResponse(status_code=200,content=data)
