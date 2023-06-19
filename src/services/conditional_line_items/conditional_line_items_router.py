from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from params import *
from rms_utils.auth import authorize_token
import sentry_sdk
from fastapi import HTTPException

from services.conditional_line_items.interaction.create_conditional_line_items import create_conditional_line_items
from services.conditional_line_items.interaction.get_conditional_line_items import get_conditional_line_items
from services.conditional_line_items.interaction.update_conditional_line_items import update_conditional_line_items
from services.conditional_line_items.interaction.delete_conditional_line_items import delete_conditional_line_items
conditional_line_items_router = APIRouter()

@conditional_line_items_router.post("/create_conditional_line_items")
def create_conditional_line_items_data(request: CreateConditionalLineItems, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = create_conditional_line_items(request.dict(exclude_none=False))
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
       
    

@conditional_line_items_router.get("/get_conditional_line_items")
def get_conditional_line_items_data(
    trade_type: str,
    port_id: str = None,
    main_port_id: str = None,
    container_size: str = None,
    container_type: str = None,
    commodity: str = None,
    shipping_line_id: str = None,
    country_id: str = None,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        request = {
            'port_id':port_id,
            'main_port_id':main_port_id,
            'country_id': country_id,
            'container_size' : container_size,
            'container_type' : container_type,
            'commodity' : commodity,
            'shipping_line_id' : shipping_line_id,
            'trade_type':trade_type
        }

        data = get_conditional_line_items(request)
        data = jsonable_encoder(data)
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })


@conditional_line_items_router.post("/update_conditional_line_items")
def update_conditional_line_item_data(request: UpdateConditionalLineItems, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = update_conditional_line_items(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@conditional_line_items_router.post("/delete_conditional_line_items")
def delete_conditional_line_items_data(request: DeleteConditionalLineItems, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        delete_rate = delete_conditional_line_items(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(delete_rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })