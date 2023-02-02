from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from database.db_session import db
from fastapi import FastAPI, Response, Query, Request, Depends
from services.fcl_freight_rate.interaction.get_fcl_freight_rate import get_fcl_freight_rate
# from database.create_tables import create_table
from services.fcl_freight_rate.interaction.create_fcl_freight_rate import create_fcl_freight_rate_data
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_local import create_fcl_freight_rate_local_data
from services.fcl_freight_rate.models.fcl_freight_rates import postFclFreightRate
from celery_worker import create_task
from services.fcl_freight_rate.models.fcl_freight_rate_locals import postFclFreightRateLocal


app = FastAPI(debug=True)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    # db.connect()
    # create_table()
    print("connected")
    
@app.on_event("shutdown")
def shutdown():
    if not db.is_closed():
        db.close()

@app.get("/")
def read_root():
    return "WELCOME TO OCEAN RMS"

@app.get("/get_fcl_freight_rate_data")
def get_fcl_freight_rate_data():
    data = get_fcl_freight_rate()
    data = jsonable_encoder(data)
    return JSONResponse(status_code=200, content=data)

@app.post("/create_fcl_freight_rate")
def create_fcl_freight_rate(request: postFclFreightRate, response: Response):
    # try:
        rate = create_fcl_freight_rate.delay(request.dict(exclude_none=True))
        # return create_fcl_freight_rate(request.dict(exclude_none=True))
        # return JSONResponse(status_code=200, content=data)
        return JSONResponse(status_code=200, content={"success": True})
    # except Exception as e:
        # logger.error(e,exc_info=True)
    #     return JSONResponse(status_code=500, content={"success": False})

@app.post("/create_fcl_freight_rate_local")
def create_fcl_freight_rate(request: postFclFreightRateLocal, response: Response):
    return create_fcl_freight_rate_local_data(request)