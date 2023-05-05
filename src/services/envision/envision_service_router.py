from fastapi import APIRouter
from fastapi.responses import JSONResponse
from services.envision.envision_params import *
from services.envision.interaction.get_ftl_freight_predicted_rate import predict_ftl_freight_rate
from services.envision.interaction.create_ftl_freight_rate_prediction_feedback import (
    create_ftl_freight_rate_feedback
)
from services.envision.interaction.create_air_freight_rate_prediction_feedback import create_air_freight_rate_feedback
from services.envision.interaction.get_air_freight_predicted_rate import predict_air_freight_rate
from services.envision.interaction.get_haulage_freight_predicted_rate import predict_haulage_freight_rate
from services.envision.interaction.create_haulage_freight_rate_prediction_feedback import (
    create_haulage_freight_rate_feedback
)
from fastapi.encoders import jsonable_encoder

envision_router = APIRouter()

@envision_router.post("/get_ftl_freight_predicted_rate")
def get_ftl_freight_predicted_rate(request: FtlFreightRate):
    result = []
    try:
        for param in request.params:
            try:
                param = predict_ftl_freight_rate(param)
            except:
                param = param.__dict__
                param["predicted_price"] = None
        result.append(param)
        data = create_ftl_freight_rate_feedback(result)
    except:
        return JSONResponse(status_code = 500, content = jsonable_encoder({'success':False, 'data':data}))
    if data.get('success'):
        return JSONResponse(status_code = 200, content=jsonable_encoder(data))
    else:
        return JSONResponse(status_code = 500, content = jsonable_encoder(data))

@envision_router.post("/get_haulage_freight_predicted_rate")
def get_haulage_freight_predicted_rate(request: HaulageFreightRate):
    result = []
    try:
        for param in request.params:
            try:
                param = predict_haulage_freight_rate(param)
            except:
                param = param.__dict__
                param["predicted_price"] = None
        result.append(param)
        data = create_haulage_freight_rate_feedback(result)
    except:
        return JSONResponse(status_code = 500, content = jsonable_encoder({'success':False, 'data':data}))
    if data.get('success'):
        return JSONResponse(status_code = 200, content=jsonable_encoder(data))
    else:
        return JSONResponse(status_code = 500, content = jsonable_encoder(data))

@envision_router.post("/get_air_freight_predicted_rate")
def get_air_freight_predicted_rate(request: AirFreightRate):
    result = []
    try:
        for param in request.params:
            try:
                param = predict_air_freight_rate(param)
            except:
                param = param.__dict__
                param["predicted_price"] = None
        result.append(param)
        data = create_air_freight_rate_feedback(result)
    except:
        return JSONResponse(status_code = 500, content = jsonable_encoder({'success':False, 'data':data}))
    if data.get('success'):
        return JSONResponse(status_code = 200, content=jsonable_encoder(data))
    else:
        return JSONResponse(status_code = 500, content = jsonable_encoder(data))
