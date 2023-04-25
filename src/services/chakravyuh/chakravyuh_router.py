from services.chakravyuh.interaction.create_fcl_freight_rate_estimation import create_fcl_freight_rate_estimation
from params import CreateFclEstimatedRate
from rms_utils.auth import authorize_token
from fastapi import APIRouter, Query, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from services.chakravyuh.migrating_estimated_rates import migration_of_countries

chakravyuh_router = APIRouter()

@chakravyuh_router.post("/create_fcl_estimated_rate")
def create_fcl_estimated_rates(request: CreateFclEstimatedRate, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    estimated_rate = create_fcl_freight_rate_estimation(request.dict(exclude_none=True))
    return JSONResponse(status_code=200, content=jsonable_encoder(estimated_rate))


@chakravyuh_router.post("/migrating")
def migration():
    migration_of_countries()

