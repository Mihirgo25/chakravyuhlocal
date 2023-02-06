from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from database.db_session import db
from services.fcl_freight_rate.interaction.get_fcl_freight_rate import get_fcl_freight_rate
from services.fcl_freight_rate.interaction.list_fcl_freight_rates import list_fcl_freight_rates
from services.fcl_freight_rate.interaction.get_fcl_freight_rate_local import get_fcl_freight_rate_local
from params import ListFclFreightRate, GetFclFreightRateLocal
from services.fcl_freight_rate.interaction.test_fcl_freight_rate import test_fcl

app = FastAPI(debug=True)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    db.connect()
    print("connected")
    
@app.on_event("shutdown")
def shutdown():
    if not db.is_closed():
        db.close()

@app.get("/")
def read_root():
    return "WELCOME TO OCEAN RMS"

# @app.get("/get_fcl_freight_rate_data")
# def get_fcl_freight_rate_data():
#     data = get_fcl_freight_rate()
#     data = jsonable_encoder(data)
#     return JSONResponse(status_code=200, content=data)

@app.post("/list_fcl_freight_rates")
def list_fcl_freight_data(request: ListFclFreightRate):
    data = list_fcl_freight_rates(request)
    return None

@app.post("/get_fcl_freight_rate_local")
def get_fcl_freight_card(request: GetFclFreightRateLocal):
    data = get_fcl_freight_rate_local(request)
    return None

