from fastapi import APIRouter
from services.rate_sheet.interactions.create_rate_sheet import create_rate_sheet
from services.rate_sheet.interactions.update_rate_sheet import update_rate_sheet
from services.rate_sheet.interactions.list_rate_sheets import list_rate_sheets
from fastapi.responses import JSONResponse
from fastapi import  Response
from params import *

rate_sheet = APIRouter()


@rate_sheet.post("/create_rate_sheet")
def create_rate_sheets(request: CreateRateSheet, response: Response):
    rate_sheet = create_rate_sheet(request.dict(exclude_none=True))
    return JSONResponse(status_code=200, content=rate_sheet)



@rate_sheet.post("/update_rate_sheet")
def update_rate_sheets(request: UpdateRateSheet, response: Response):
    rate_sheet =update_rate_sheet(request.dict(exclude_none=True))
    return JSONResponse(status_code=200, content=rate_sheet)


@rate_sheet.get("/list_rate_sheets")
def list_rates_sheets(
    filters: str = None,
    stats_required: bool = True,
    page: int = 1,
    page_limit: int = 10,
    sort_by: str = 'created_at',
    sort_type: str = 'desc',
    pagination_data_required:  bool = True,


):
    response = list_rate_sheets(
        filters, stats_required, page, page_limit,sort_by, sort_type, pagination_data_required
    )
    return JSONResponse(status_code=200, content=response)
