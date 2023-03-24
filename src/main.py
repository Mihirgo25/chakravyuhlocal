from fastapi import FastAPI,  Request
from fastapi.middleware.cors import CORSMiddleware

from database.db_session import db
from fastapi import FastAPI, Request
from configs.env import APP_ENV
from params import *
from fastapi.responses import JSONResponse

from services.fcl_freight_rate.fcl_freight_router import fcl_freight_router

docs_url = None if APP_ENV == "production" else "/docs"

app = FastAPI(docs_url=docs_url,debug=True)


app.include_router(prefix = "/fcl_freight_rate_v2", router=fcl_freight_router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_request_response_time(request: Request, call_next):
    from time import time
    start_time = time()
    response = await call_next(request)
    process_time = time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.on_event("startup")
def startup():
    if db.is_closed():
        db.connect()
    # create_table()
    # initialize_client()

@app.on_event("shutdown")
def shutdown():
    if not db.is_closed():
        db.close()

@app.get("/")
def read_root():
    return "WELCOME TO OCEAN RMS"

@app.get('/fcl_freight_rate_v2/health_check')
def get_health_check():
    return JSONResponse(status_code=200, content={ "status": 'healthy' })
