from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from database.db_session import db
from fastapi import FastAPI, Response, Query, Request, Depends
from services.fcl_freight_rate.interaction.get_fcl_freight_rate import get_fcl_freight_rate
#from database.create_tables import create_table
from services.fcl_freight_rate.interaction.create_fcl_freight_rate import create_fcl_freight_rate_data
from services.fcl_freight_rate.interaction.delete_fcl_freight_rate import delete_fcl_freight_rate
from services.fcl_freight_rate.interaction.extend_create_fcl_freight_rate import extend_create_fcl_freight_rate_data
from services.fcl_freight_rate.interaction.update_fcl_freight_rate_extension_rule_set import update_fcl_freight_rate_extension_rule_set_data
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_extension_rule_sets import list_fcl_freight_rate_extension_rule_set_data
from services.fcl_freight_rate.interaction.update_fcl_freight_rate_local_priority_scores import update_fcl_freight_rate_local_priority_scores_data
from services.fcl_freight_rate.interaction.update_fcl_freight_rate_priority_scores import update_fcl_freight_rate_priority_scores_data
from services.fcl_freight_rate.interaction.update_fcl_freight_rate_task import update_fcl_freight_rate_task_data
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_extension_rule_set import create_fcl_freight_rate_extension_rule_set_data
from services.fcl_freight_rate.interaction.get_fcl_freight_rate_extension import get_fcl_freight_rate_extension_data
from services.fcl_freight_rate.interaction.update_fcl_freight_rate import update_fcl_freight_rate_data
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_local import create_fcl_freight_rate_local_data
from services.fcl_freight_rate.interaction.update_fcl_freight_rate_local import update_fcl_freight_rate_local_data
# from services.fcl_freight_rate.interaction.create_fcl_freight_rate_task import create_fcl_freight_rate_task_data
from services.fcl_freight_rate.interaction.delete_fcl_freight_rate_request import delete_fcl_freight_rate_request
from services.fcl_freight_rate.interaction.delete_fcl_freight_rate_feedback import delete_fcl_freight_rate_feedback
from services.fcl_freight_rate.interaction.delete_fcl_freight_rate_local_request import delete_fcl_freight_rate_local_request
from services.fcl_freight_rate.interaction.delete_fcl_freight_rate_local import delete_fcl_freight_rate_local
from services.fcl_freight_rate.interaction.delete_fcl_freight_rate_free_day_request import delete_fcl_freight_rate_free_day_request
from rails_client.client import initialize_client
from params import *
from database.create_tables import create_table

# from services.fcl_freight_rate.interaction.list_fcl_freight_rates import list_fcl_freight_rates
# from services.fcl_freight_rate.interaction.get_fcl_freight_rate_local import get_fcl_freight_rate_local


app = FastAPI(debug=True)


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
    initialize_client()
    
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

# @app.post("/list_fcl_freight_rates")
# def list_fcl_freight_data(request: ListFclFreightRate):
#     data = list_fcl_freight_rates(request)
#     return None

# @app.post("/get_fcl_freight_rate_local")
# def get_fcl_freight_card(request: GetFclFreightRateLocal):
#     data = get_fcl_freight_rate_local(request)
#     return None

@app.post("/create_fcl_freight_rate")
def create_fcl_freight_rate(request: PostFclFreightRate, response: Response):
    # try:
        rate = create_fcl_freight_rate_data(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(rate))
    # except Exception as e:
        # logger.error(e,exc_info=True)
    #     return JSONResponse(status_code=500, content={"success": False})

@app.post("/create_fcl_freight_rate_local")
def create_fcl_freight_rate(request: PostFclFreightRateLocal, response: Response):
    return create_fcl_freight_rate_local_data(request)

@app.post("/update_fcl_freight_rate")
def update_fcl_freight_rate(request: UpdateFclFreightRate, response: Response):
    rate = update_fcl_freight_rate_data(request.dict(exclude_none=True))
    return JSONResponse(status_code=200, content={"success": True})

@app.post("/update_fcl_freight_rate_local")
def update_fcl_freight_rate_local(request: UpdateFclFreightRateLocal, response: Response):
    return update_fcl_freight_rate_local_data(request.dict(exclude_none=True))

@app.delete("/delete_fcl_freight_rate")
def delete_fcl_freight_rates(request: DeleteFclFreightRate, response: Response):
    delete_rate = delete_fcl_freight_rate(request.dict(exclude_none=True))
    return JSONResponse(status_code=200, content={"success": True})

@app.post("/create_fcl_freight_rate_exclusive_rule_set")
def create_fcl_freight_rate_extension_rule_set(request: PostFclFreightRateExtensionRuleSet):
    return create_fcl_freight_rate_extension_rule_set_data(request)

@app.post("/extend_create_fcl_freight_rate")
def extend_create_fcl_freight_rate(request: ExtendCreateFclFreightRate):
    return extend_create_fcl_freight_rate_data(request)

@app.post("/update_fcl_freight_rate_extension_rule_set")
def update_fcl_freight_rate_extension_rule_set(request: UpdateFclFreightRateExtensionRuleSet):
    return update_fcl_freight_rate_extension_rule_set_data(request)

@app.post("/list_fcl_freight_rate_extension_rule_set")
def list_fcl_freight_rate_extension_rule_set(request: ListFclFreightRateExtensionRuleSets):
    return list_fcl_freight_rate_extension_rule_set_data(request)

@app.post("/get_fcl_freight_rate_extension")
def get_fcl_freight_rate_extension(request: GetFclFreightRateExtension):
    return get_fcl_freight_rate_extension_data(request)

@app.post("/update_fcl_freight_rate_task")
def update_fcl_freight_rate_task(request: UpdateFclFreightRateTask):
    return update_fcl_freight_rate_task_data(request)

# @app.post("/create_fcl_freight_rate_task")
# def create_fcl_freight_rate_task(request: CreateFclFreightRateTask):
#     return create_fcl_freight_rate_task_data(request)

@app.delete("/delete_fcl_freight_rate_request")
def delete_fcl_freight_rates_request(request: DeleteFclFreightRateRequest, response: Response):
    delete_rate = delete_fcl_freight_rate_request(request.dict(exclude_none=True))
    return JSONResponse(status_code=200, content={"success": True})

@app.delete("/delete_fcl_freight_rate_feedback")
def delete_fcl_freight_rates_feedback(request: DeleteFclFreightRateFeedback, response: Response):
    delete_rate = delete_fcl_freight_rate_feedback(request.dict(exclude_none=True))
    return JSONResponse(status_code=200, content={"success": True})

@app.delete("/delete_fcl_freight_rate_local_request")
def delete_fcl_freight_rates_local_request(request: DeleteFclFreightRateLocalRequest, response: Response):
    delete_rate = delete_fcl_freight_rate_local_request(request.dict(exclude_none=True))
    return JSONResponse(status_code=200, content={"success": True})

@app.delete("/delete_fcl_freight_rate_local")
def delete_fcl_freight_rates_local(request: DeleteFclFreightRateLocal, response: Response):
    delete_rate = delete_fcl_freight_rate_local(request.dict(exclude_none=True))
    return JSONResponse(status_code=200, content={"success": True})

@app.delete("/delete_fcl_freight_rate_free_day_request")
def delete_fcl_freight_rates_free_day_request(request: DeleteFclFreightRateFreeDayRequest, response: Response):
    delete_rate = delete_fcl_freight_rate_free_day_request(request.dict(exclude_none=True))
    return JSONResponse(status_code=200, content={"success": True})
