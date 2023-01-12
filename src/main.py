from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from database.db_session import db
from services.fcl_freight_rate.interaction.get_fcl_freight_rate import get_fcl_freight_rate

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
    
@app.on_event("shutdown")
def shutdown():
    if not db.is_closed():
        db.close()

@app.get("/")
def read_root():
    return "WELCOME TO RATE AUTOMATION WORLD"

@app.get("/get_fcl_freight_rate_data")
def get_fcl_freight_rate_data():
    data = get_fcl_freight_rate()
    return JSONResponse(status_code=200, content=data)

