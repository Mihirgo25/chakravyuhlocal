from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
import sentry_sdk
from database.db_session import db
from fastapi import FastAPI, Request
from configs.env import APP_ENV, SENTRY_DSN
from fastapi import HTTPException
from params import *
from fastapi.responses import JSONResponse

# from database.create_tables import create_table
# from services.haulage_freight_rate.datamigrations.inserting_rule_set_data import insert, insert_china
# from libs.migration import fcl_freight_migration, create_partition_table, fcl_local_migration,free_day
# from database.db_migration import run_migration
from services.fcl_freight_rate.fcl_freight_router import fcl_freight_router
from services.chakravyuh.chakravyuh_router import chakravyuh_router
from services.nandi.nandi_router import nandi_router
from services.ftl_freight_rate.ftl_freight_router import ftl_freight_router
from services.envision.envision_service_router import envision_router
from services.chakravyuh.chakravyuh_router import chakravyuh_router
from services.trailer_freight_rate.trailer_freight_router import trailer_router
from services.haulage_freight_rate.haulage_freight_rate_router import haulage_freight_router
from services.extensions.extension_router import extension_router
from services.air_customs_rate.air_customs_router import air_customs_router

from services.fcl_customs_rate.fcl_customs_rate_router import fcl_customs_router
from services.fcl_cfs_rate.fcl_cfs_router import fcl_cfs_router
from services.air_freight_rate.air_freight_rate_router import air_freight_router
from micro_services.client import *
from database.db_support import get_db


sentry_sdk.init(
    dsn=SENTRY_DSN if APP_ENV == "production" else None,
    environment="production",
    traces_sample_rate=0.5,
    attach_stacktrace=True,
    ignore_errors=[HTTPException],
)

docs_url = None if APP_ENV == "production" else "/docs"

app = FastAPI(docs_url=docs_url, debug=True,dependencies=[Depends(get_db)])


app.include_router(prefix = "/fcl_freight_rate", router=fcl_freight_router, tags=['Fcl Freight Rate'])
app.include_router(prefix = "/fcl_freight_rate", router=ftl_freight_router, tags=['FTL Freight Rate'])
app.include_router(prefix="/fcl_freight_rate", router=envision_router, tags=['Predictions'])
app.include_router(prefix = "/fcl_freight_rate", router=chakravyuh_router, tags=['Chakravyuh'])
app.include_router(prefix="/fcl_freight_rate", router=trailer_router, tags=['Trailer Freight Rate'])
app.include_router(prefix="/fcl_freight_rate", router=nandi_router, tags=['Error Detection (Nandi)'])
app.include_router(prefix = "/fcl_freight_rate", router=haulage_freight_router, tags=['Haulage Freight Rate'])
app.include_router(prefix = "/fcl_freight_rate", router=extension_router, tags=['Web Extensions'])
app.include_router(prefix = "/fcl_customs_rate", router=fcl_customs_router, tags = ['Fcl Customs Rate'])
app.include_router(prefix = "/fcl_cfs_rate", router=fcl_cfs_router, tags = ['Fcl Cfs Rate'])

app.include_router(prefix = "/air_freight_rate",router = air_freight_router, tags = ['Air Freight Rate'])
app.include_router(prefix = "/air_customs_rate", router=air_customs_router, tags = ['Air Customs Rate'])


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


if APP_ENV != "production":

    async def set_client_base_url(request: Request, call_next):
        url = request.headers.get("dev_server_url")
        if url:
            common.reset_context_var(url)
            organization.reset_context_var(url)
            partner.reset_context_var(url)
            maps.reset_context_var(url)
            spot_search.reset_context_var(url)
            checkout.reset_context_var(url)
            shipment.reset_context_var(url)
        response = await call_next(request)
        return response

    app.middleware("http")(set_client_base_url)

if APP_ENV != "production":

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
    # insert_wagon_type()
    # insert_dbcargo_rates()
    # insert_france_germany_rates()
    # create_rail_haulage_rates()
    # insert()
    # insert_china()
    # run_migration()
    # create_table()
    # fcl_freight_migration()
    # create_partition_table()
    # fcl_local_
    # migration()
    # free_day()


@app.on_event("shutdown")
def shutdown():
    if not db.is_closed():
        db.close()


@app.get("/")
def read_root():
    return "WELCOME TO OCEAN RMS"


@app.get("/fcl_freight_rate/health")
def get_health_check():
    return JSONResponse(status_code=200, content={ "status": 'ok' })

@app.get("/fcl_freight_rate/health_check")
def get_health_check():
    return JSONResponse(status_code=200, content={ "status": 'ok' })
