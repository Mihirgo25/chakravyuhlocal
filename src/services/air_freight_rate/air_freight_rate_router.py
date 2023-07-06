from fastapi import APIRouter, Depends, HTTPException
from rms_utils.auth import authorize_token
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from services.air_freight_rate.air_freight_rate_params import *
from params import CreateRateSheet, UpdateRateSheet
import sentry_sdk
from datetime import datetime
from rms_utils.auth import authorize_token
import json

extension_router = APIRouter()

from services.air_freight_rate.interactions.create_draft_air_freight_rate import create_draft_air_freight_rate
from services.air_freight_rate.interactions.get_air_freight_storage_rate import get_air_freight_storage_rate
from services.air_freight_rate.interactions.delete_air_freight_rate_local import delete_air_freight_rate_local
from services.air_freight_rate.interactions.delete_air_freight_rate_feedback import delete_air_freight_rate_feedback
from services.air_freight_rate.interactions.create_air_freight_rate import create_air_freight_rate
from services.air_freight_rate.interactions.list_air_freight_warehouse_rates import list_air_freight_warehouse_rates
from services.air_freight_rate.interactions.delete_air_freight_rate import delete_air_freight_rate
from services.air_freight_rate.interactions.update_air_freight_rate import update_air_freight_rate
from services.air_freight_rate.interactions.get_air_freight_rate import get_air_freight_rate
from services.air_freight_rate.interactions.list_air_freight_rate_surcharges import list_air_freight_rate_surcharges
from services.air_freight_rate.interactions.create_air_freight_rate_surcharge import create_air_freight_rate_surcharge
from services.air_freight_rate.interactions.create_air_freight_rate_local import create_air_freight_rate_local
from services.air_freight_rate.interactions.update_air_freight_rate_surcharge import update_air_freight_rate_surcharge
from services.air_freight_rate.interactions.create_air_freight_rate_task import create_air_freight_rate_task
from services.air_freight_rate.interactions.get_air_freight_rate_local import get_air_freight_rate_local
from services.air_freight_rate.interactions.get_air_freight_rate_cards import get_air_freight_rate_cards
from services.air_freight_rate.interactions.update_air_freight_rate_local import update_air_freight_rate_local
from services.air_freight_rate.interactions.list_air_freight_rate_locals import list_air_freight_rate_locals
from services.air_freight_rate.interactions.update_air_freight_rate_task import update_air_freight_rate_task
from services.air_freight_rate.interactions.create_air_freight_rate_request import create_air_freight_rate_request
from services.air_freight_rate.interactions.get_air_freight_rate_stats import get_air_freight_rate_stats
from services.air_freight_rate.interactions.create_air_freight_rate_not_available import create_air_freight_rate_not_available
from services.air_freight_rate.interactions.create_air_freight_storage_rate import create_air_freight_storage_rate
from services.air_freight_rate.interactions.get_air_freight_rate_visibility import get_air_freight_rate_visibility
from services.air_freight_rate.interactions.get_air_freight_rate_addition_frequency import get_air_freight_rate_addition_frequency 
from services.air_freight_rate.interactions.get_air_freight_warehouse_rate import get_air_freight_warehouse_rate
from services.air_freight_rate.interactions.create_air_freight_warehouse_rate import create_air_freight_warehouse_rate
from services.air_freight_rate.interactions.update_air_freight_warehouse_rate import update_air_freight_warehouse_rate
from services.air_freight_rate.interactions.list_air_freight_rate_feedbacks import list_air_freight_rate_feedbacks
from services.air_freight_rate.interactions.list_air_freight_rate_requests import list_air_freight_rate_requests
from services.air_freight_rate.interactions.list_air_freight_rate_dislikes import list_air_freight_rate_dislikes
from services.air_freight_rate.interactions.list_air_freight_charge_codes import list_air_freight_charge_codes
from services.air_freight_rate.interactions.update_air_freight_rate_markup import update_air_freight_rate_markup
from services.air_freight_rate.interactions.list_air_freight_rates import list_air_freight_rates
from services.air_freight_rate.interactions.create_air_freight_rate_bulk_operation import create_air_freight_rate_bulk_operation
from services.air_freight_rate.interactions.get_air_freight_local_rate_cards import get_air_freight_local_rate_cards
from services.air_freight_rate.interactions.get_weight_slabs_for_airline import get_weight_slabs_for_airline
from services.air_freight_rate.interactions.create_air_freight_rate_feedback import create_air_freight_rate_feedback
from services.air_freight_rate.interactions.delete_air_freight_rate_request import delete_air_freight_rate_request
from services.air_freight_rate.interactions.delete_air_freight_rate_surcharge import delete_air_freight_rate_surcharge
from services.air_freight_rate.interactions.get_air_freight_rate_surcharge import get_air_freight_rate_surcharge
from services.rate_sheet.interactions.create_rate_sheet import create_rate_sheet
from services.rate_sheet.interactions.update_rate_sheet import update_rate_sheet
from services.rate_sheet.interactions.list_rate_sheets import list_rate_sheets
from services.rate_sheet.interactions.list_rate_sheet_stats import list_rate_sheet_stats
from services.air_freight_rate.interactions.get_air_freight_rate_suggestions import get_air_freight_rate_suggestions
from services.air_freight_rate.interactions.update_air_freight_storage_rate import update_air_freight_storage_rate
from services.air_freight_rate.interactions.get_air_freight_rate_audit import get_air_freight_rate_audit
from services.air_freight_rate.interactions.update_air_freight_rate_request import update_air_freight_rate_request
from services.air_freight_rate.interactions.list_air_freight_rate_tasks import list_air_freight_rate_tasks

air_freight_router = APIRouter()


@air_freight_router.post("/create_air_freight_rate")
def create_air_freight_rate_api(request: CreateAirFreightRateParams, resp: dict = Depends(authorize_token)):
    if resp["status_code"]!=200:
        return JSONResponse(status_code=resp['status_code'],content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        create_rate=create_air_freight_rate(request.dict())
        return JSONResponse(status_code=200,content=jsonable_encoder(create_rate))
    except HTTPException as e :
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@air_freight_router.post("/delete_air_freight_rate")
def delete_air_freight_rate_api(request: DeleteAirFreightRateParams, resp: dict = Depends(authorize_token)):
    if resp["status_code"]!=200:
        return JSONResponse(status_code=resp['status_code'],content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        delete_rate=delete_air_freight_rate(request.dict(exclude_none=True))
        return JSONResponse(status_code=200,content=jsonable_encoder(delete_rate))
    except HTTPException as e :
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@air_freight_router.post("/update_air_freight_rate")
def update_air_freight_rate_api(
    request: UpdateAirFreightRateParams, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]

        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = update_air_freight_rate(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })


@air_freight_router.get("/get_air_freight_rate")
def get_air_freight_rate_api(
    origin_airport_id: str = None,
    destination_airport_id: str = None,
    commodity: str = None,
    commodity_type: str = None,
    commodity_sub_type: str = None,
    airline_id: str = None,
    operation_type: str = None,
    service_provider_id: str = None,
    shipment_type: str = "box",
    stacking_type: str = "stackable",
    validity_start: datetime = None,
    validity_end: datetime = None,
    weight: float = None,
    cargo_readiness_date: date = None,
    price_type: str = None,
    cogo_entity_id: str = None,
    trade_type: str = None,
    volume: float = None,
    chargeable_weight:float =None,
    predicted_rates_required: bool = False,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    request = {
        "origin_airport_id": origin_airport_id,
        "destination_airport_id": destination_airport_id,
        "commodity": commodity,
        "commodity_type": commodity_type,
        "commodity_sub_type": commodity_sub_type,
        "airline_id": airline_id,
        "operation_type": operation_type,
        "shipment_type": shipment_type,
        "service_provider_id": service_provider_id,
        "stacking_type": stacking_type,
        "cogo_entity_id": cogo_entity_id,
        "validity_start": validity_start,
        "validity_end": validity_end,
        "weight": weight,
        "cargo_readiness_date": cargo_readiness_date,
        "price_type": price_type,
        "trade_type": trade_type,
        "volume": volume,
        "chargeable_weight":chargeable_weight,
        "predicted_rates_required": predicted_rates_required
    }

    try:
        data = get_air_freight_rate(request)
        data = jsonable_encoder(data)
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@air_freight_router.get("/get_air_freight_rate_local")
def get_air_freight_rate_local_api(
    airport_id: str = None,
    airline_id: str = None,
    trade_type: str = None,
    commodity: str = None,
    service_provider_id: str = None,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    request = {
        "airport_id": airport_id,
        "airline_id": airline_id,
        "trade_type": trade_type,
        "commodity": commodity,
        "service_provider_id": service_provider_id,
    }

    try:
        data = get_air_freight_rate_local(request)
        data = jsonable_encoder(data)
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@air_freight_router.get("/get_air_freight_rate_visibility")
def get_air_freight_rate_visibility_api(
    service_provider_id: str,
    origin_location_id: str = None,
    destination_location_id: str = None,
    from_date: date = None,
    to_date: date = None,
    commodity: str = None,
    rate_id: str = None,
    airline_id: str = None,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    request = {
        "service_provider_id": service_provider_id,
        "origin_location_id": origin_location_id,
        "destination_location_id": destination_location_id,
        "from_date": from_date,
        "to_date": to_date,
        "commodity": commodity,
        "rate_id": rate_id,
        "airline_id": airline_id,
        "service_provider_id": service_provider_id,
    }

    try:
        data = get_air_freight_rate_visibility(request)
        data = jsonable_encoder(data)
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@air_freight_router.get("/get_air_freight_rate_addition_frequency")
def get_air_freight_rate_addition_frequency_api(
    group_by: str = 'week',
    filters: str = None,
    sort_type: str = "desc", 
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    
    try:
        data = get_air_freight_rate_addition_frequency(group_by= group_by,filters = filters,sort_type = sort_type)
        data = jsonable_encoder(data)
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@air_freight_router.post("/update_air_freight_rate_local")
def update_air_freight_rate_local_api(
    request: UpdateAirFrieghtRateLocalParams, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]

    try:
        data = update_air_freight_rate_local(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@air_freight_router.post("/create_air_freight_rate_not_available")
def create_air_freight_rate_not_available_api(
    request: CreateAirFrieghtRateNotAvailableParams, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = create_air_freight_rate_not_available(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@air_freight_router.post("/create_air_freight_rate_local")
def create_air_freight_rate_local_api(
    request: CreateAirFreightRateLocalParams, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]

    try:
        data = create_air_freight_rate_local(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@air_freight_router.post("/create_air_freight_rate_surcharge")
def create_air_freight_rate_surcharge_api(
    request: CreateAirFreightRateSurchargeParams, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]

    try:
        data = create_air_freight_rate_surcharge(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@air_freight_router.get("/list_air_freight_rate_locals")
def list_air_freight_rate_locals_api(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    sort_by: str = "updated_at",
    sort_type: str = "desc",
    return_query: bool = False,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = list_air_freight_rate_locals(filters = filters,
                                            page_limit= page_limit,
                                            page=page,
                                            sort_by= sort_by,
                                            sort_type= sort_type, 
                                            return_query= return_query)
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })


@air_freight_router.post("/update_air_freight_rate_surcharge")
def update_air_freight_rate_surcharge_api(
    request: UpdateAirFreightRateSurchargeParams, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]

    try:
        data = update_air_freight_rate_surcharge(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@air_freight_router.get("/get_air_freight_rate_surcharge")
def get_air_freight_rate_surcharge_api(
    origin_airport_id: str = None,
    destination_airport_id: str = None,
    commodity: str = None,
    airline_id: str = None,
    operation_type: str = None,
    service_provider_id: str = None,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    request = {
        "origin_airport_id": origin_airport_id,
        "destination_airport_id": destination_airport_id,
        "commodity": commodity,
        "airline_id": airline_id,
        "operation_type": operation_type,
        "service_provider_id": service_provider_id,
    }

    try:
        data = get_air_freight_rate_surcharge(request)
        data = jsonable_encoder(data)
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@air_freight_router.post("/create_air_freight_rate_task")
def create_air_freight_rate_task_api(
    request: CreateAirFreightRateTaskParams, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    
    try:
        data = create_air_freight_rate_task(request.dict(exclude_none=False))
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@air_freight_router.get("/list_air_freight_rate_surcharges")
def list_air_freight_rate_surcharges_api(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    pagination_data_required: bool = True,
    return_query: bool = True,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        data = list_air_freight_rate_surcharges(filters=filters, 
                                                page_limit=page_limit, 
                                                page=page, 
                                                pagination_data_required=pagination_data_required,
                                                return_query=return_query)
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@air_freight_router.post("/update_air_freight_rate_task")
def update_air_freight_rate_task_api(
    request: UpdateAirFreightRateTaskParams, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp['isAuthorized']:
        request.performed_by_id = resp["setters"]["performed_by_id"]
    try:
        return JSONResponse(
            status_code=200,
            content=update_air_freight_rate_task(request.dict(exclude_none=False)),
        )
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )
        

@air_freight_router.get("/get_air_freight_rate_cards")
def get_air_freight_rate_cards_api(
    origin_airport_id: str,
    destination_airport_id: str,
    validity_start: datetime,
    cargo_clearance_date: date,
    validity_end: datetime,
    packages_count: int,
    trade_type: str,
    weight: float,
    volume: float,
    commodity: str = "general",
    commodity_type: str = "all",
    commodity_sub_type: str = None,
    commodity_sub_type_code: str = None,
    airline_id: str = None,
    packing_type: str = "box",
    handling_type: str = "stackable",
    price_type: str = None,
    cogo_entity_id: str = None,
    additional_services: str = None,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    request = {
        "origin_airport_id": origin_airport_id,
        "destination_airport_id": destination_airport_id,
        "commodity": commodity,
        "airline_id": airline_id,
        "cargo_clearance_date": cargo_clearance_date,
        "validity_end": validity_end,
        "validity_start": validity_start,
        "weight": weight,
        "volume": volume,
        "commodity_type": commodity_type,
        "cogo_entity_id": cogo_entity_id,
        "additional_services": additional_services,
        "commodity_sub_type": commodity_sub_type,
        "commodity_sub_type_code": commodity_sub_type_code,
        "price_type": price_type,
        "packages_count": packages_count,
        "trade_type": trade_type,
        "packing_type": packing_type,
        "handling_type": handling_type,
    }

    try:
        if additional_services:
            request['additional_services'] = json.loads(additional_services)
        data = get_air_freight_rate_cards(request)
        data = jsonable_encoder(data)
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })


@air_freight_router.post("/create_air_freight_rate_request")
def create_air_freight_rate_request_api(
    request: CreateAirFreightRateRequestParams, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        return JSONResponse(
            status_code=200,
            content=create_air_freight_rate_request(request.dict(exclude_none=False)),
        )
    except HTTPException as h:
        raise
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@air_freight_router.get("/get_air_freight_rate_stats")
def get_air_freight_rate_stats_api(
    validity_start: datetime,
    validity_end: datetime,
    stats_types: str,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    request = {
        "validity_start": validity_start,
        "validity_end": validity_end,
        'stats_types':json.loads(stats_types),
    }
    try:
        data = get_air_freight_rate_stats(request)
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@air_freight_router.post("/create_air_freight_warehouse_rate")
def create_air_freight_warehouse_rate_api(
    request: CreateAirFreightWarehouseRatesParams, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        return JSONResponse(
            status_code=200,
            content=create_air_freight_warehouse_rate(request.dict(exclude_none=False)),
        )
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@air_freight_router.get("/list_air_freight_rate_feedbacks")
def list_air_freight_rate_feedbacks_api(
    filters: str = None,
    spot_search_details_required: bool = False,
    page_limit: int = 10,
    page: int = 1,
    performed_by_id: str = None,
    is_stats_required: bool = True,
    booking_details_required: bool = False,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        data = list_air_freight_rate_feedbacks(
            filters,
            spot_search_details_required,
            page_limit,
            page,
            performed_by_id,
            is_stats_required,
            booking_details_required,
        )
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })


@air_freight_router.get("/list_air_freight_rate_dislikes")
def list_air_freight_rate_dislikes_api(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    
    try:
        data = list_air_freight_rate_dislikes(filters, page_limit, page)
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@air_freight_router.get("/list_air_freight_rate_requests")
def list_air_freight_rate_requests_api(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    performed_by_id: str = None,
    is_stats_required: bool = True,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = list_air_freight_rate_requests(
            filters, page_limit, page, performed_by_id, is_stats_required
        )
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@air_freight_router.get("/list_air_freight_charge_codes")
def list_air_freight_charge_codes_api(
    service_type: str,
    commodity: str = None,
    commodity_type: str = None,
    commodity_sub_type: str = None,
    trade_type: str = None,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    request = {
        "service_type": service_type,
        "commodity": commodity,
        "commodity_type": commodity_type,
        "commodity_sub_type": commodity_sub_type,
        "trade_type": trade_type,
    }

    try:
        data = list_air_freight_charge_codes(request)
        data = jsonable_encoder(data)
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@air_freight_router.get("/list_air_freight_warehouse_rates")
def list_air_freight_warehouse_rates_api(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        data = list_air_freight_warehouse_rates(filters, page_limit, page)
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    
    except HTTPException as e:
        raise

    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )



@air_freight_router.post("/update_air_freight_storage_rate")
def update_air_freight_storage_rate_api(
    request: UpdateAirFreightStorageRatesParams, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        return JSONResponse(
            status_code=200,
            content=update_air_freight_storage_rate(request.dict(exclude_none=False)),
        )
    except HTTPException as h:
        raise
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )



@air_freight_router.get("/get_air_freight_rate_suggestions")
def get_air_freight_rate_suggestions_api(
    validity_start: datetime,
    validity_end: datetime,
    searched_origin_airport_id: str = None,
    searched_destination_airport_id: str = None,
    filters: str = None,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = get_air_freight_rate_suggestions(
            validity_start,
            validity_end,
            searched_origin_airport_id,
            searched_destination_airport_id,
            filters,
        )
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )

@air_freight_router.post("/create_air_freight_rate_feedback")
def create_air_freight_rate_feedback_api(request: CreateAirFreightRateFeedbackParams, resp: dict = Depends(authorize_token)):
    if resp['status_code']!=200:
        return JSONResponse(status_code=resp['status_code'],content=resp)
    
    if resp['isAuthorized']:
        request.performed_by_id = resp['setters']['performed_by_id']
        request.performed_by_type = resp['setters']['performed_by_type']
    try:
        data=create_air_freight_rate_feedback(request.dict(exclude_none=False))
        return JSONResponse(status_code=200,content=jsonable_encoder(data))
    except HTTPException as e:
        raise 
    except Exception as e:
        return JSONResponse(status_code=500,content={"success":False,'error':str(e)})
    

@air_freight_router.post("/update_air_freight_rate_markup")
def update_air_freight_rate_markup_api(
    request: UpdateAirFreightRateMarkUpParams, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
    try:
        data = update_air_freight_rate_markup(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@air_freight_router.post("/create_air_freight_rate_bulk_operation")
def create_air_freight_rate_bulk_operation_api(request: CreateBulkOperationParams, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:

        data = create_air_freight_rate_bulk_operation(request.dict(exclude_none=True))
        return JSONResponse(content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })


@air_freight_router.post("/delete_air_freight_rate_feedback")
def delete_air_freight_rate_feedback_api(
    request: DeleteAirFreightRateFeedbackParams, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
    try:
        data = delete_air_freight_rate_feedback(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@air_freight_router.post("/create_air_freight_storage_rate")
def create_air_freight_storage_rate_api(
    request: CreateAirFreightStorageRateParams, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]

    try:
        data = create_air_freight_storage_rate(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@air_freight_router.get("/get_air_freight_storage_rate")
def get_air_freight_storage_rate_api(
    airport_id: str,
    airline_id: str,
    trade_type: str,
    commodity: str,
    service_provider_id: str,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    request = {
        "airport_id": airport_id,
        "airline_id": airline_id,
        "trade_type": trade_type,
        "commodity": commodity,
        "service_provider_id": service_provider_id,
    }
    try:
        data = get_air_freight_storage_rate(request)
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@air_freight_router.get("/get_air_freight_warehouse_rate")
def get_air_freight_warehouse_rate_api(
    airport_id: str,
    trade_type: str,
    commodity: str,
    service_provider_id: str,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    request = {
        "airport_id": airport_id,
        "trade_type": trade_type,
        "commodity": commodity,
        "service_provider_id": service_provider_id,
    }
    try:
        data = get_air_freight_warehouse_rate(request)
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={"sucess": False, "error": str(e)})


@air_freight_router.post("/update_air_freight_warehouse_rate")
def update_air_freight_warehouse_rate_api(
    request: UpdateAirFreightWarehouseRateParams, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = update_air_freight_warehouse_rate(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@air_freight_router.get("/get_air_freight_rate_audit")
def get_air_freight_rate_audit_api(id: str, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    request = {"id": id}
    try:
        data = get_air_freight_rate_audit(request)
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={"sucess": False, "error": str(e)})



@air_freight_router.post("/update_air_freight_rate_request")
def update_air_freight_rate_request_api(request:UpdateAirFreightRateRequestParams, resp:dict = Depends(authorize_token)):
    if resp['status_code']!=200:
        return JSONResponse(status_code=resp['status_code'],content=resp)
    try:
        data = update_air_freight_rate_request(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500 , content={"success":False,"error":str(e)})
    
@air_freight_router.get("/list_air_freight_rates")
def list_air_freight_rates_api(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    return_query: bool = False,
    older_rates_required: bool = False,
    all_rates_for_cogo_assured: bool = False,
    sort_by: str = 'updated_at',
    sort_type: str = 'desc',
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = list_air_freight_rates(filters= filters, 
                                      page_limit =page_limit,
                                      page= page, return_query=return_query,
                                      older_rates_required= older_rates_required,
                                      all_rates_for_cogo_assured= all_rates_for_cogo_assured,
                                      sort_by=sort_by,sort_type=sort_type)
        return JSONResponse(status_code=200, content=data)
    
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@air_freight_router.get('/get_weight_slabs_for_airline')
def get_weight_slabs_for_airline_api(
    airline_id:str,
    chargeable_weight: float = 0,
    overweight_upper_limit:float =0.0,
    resp: dict = Depends(authorize_token)
    ):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = get_weight_slabs_for_airline(airline_id,chargeable_weight,overweight_upper_limit)
        return JSONResponse(status_code=200, content=data)

    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })



@air_freight_router.get("/list_air_freight_rate_tasks")
def list_air_freight_rate_tasks_api(
    filters:str=None,
    page_limit:int=10,
    page:int=1,
    sort_by :str= 'created_at',
    sort_type :str= 'desc',
    stats_required:bool= True,
    pagination_data_required :bool= True,
    resp:dict =Depends(authorize_token)):
    if resp['status_code']!=200:
        return JSONResponse(status_code=resp['status_code'],content=resp)
    try:
        data=list_air_freight_rate_tasks(filters=filters,page_limit=page_limit,page=page,sort_by=sort_by,sort_type=sort_type,stats_required=stats_required,pagination_data_required=pagination_data_required)
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e :
        print(e)
        return JSONResponse(status_code=500, content={"sucess":False,"error":str(e)})
    

@air_freight_router.get("/get_air_freight_local_rate_cards")
def get_air_freight_local_rate_cards_api(
    airport_id:str,
    trade_type:str,
    commodity :str,
    commodity_type :str,
    packages_count:int,
    weight :float,
    volume:float,
    airline_id:str=None,
    additional_services: str = None,
    inco_term:str=None,
    resp:dict =Depends(authorize_token)):
    if resp['status_code']!=200:
        return JSONResponse(status_code=resp['status_code'],content=resp)
    
    request ={
    "airport_id":airport_id,
    "trade_type": trade_type,
    "commodity": commodity,
    "commodity_type":commodity_type,
    "packages_count":packages_count,
    "weight":weight,
    "volume":volume,
    "airline_id":airline_id,
    "additional_services":additional_services,
    "inco_term":inco_term
    }
    
    try:
        if additional_services:
            request['additional_services'] = json.loads(additional_services)
        data=get_air_freight_local_rate_cards(request)
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e :
        print(e)
        return JSONResponse(status_code=500, content={"sucess":False,"error":str(e)})

@air_freight_router.post("/delete_air_freight_rate_request")
def delete_air_freight_rate_request_api(request:DeleteAirFreightRateRequestParams , resp:dict = Depends(authorize_token)):
    if resp['status_code']!=200:
        return JSONResponse(status_code=resp['statuse_code'],content=resp)
    
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]

    try:
        data=delete_air_freight_rate_request(request.dict(exclude_none=True))
        return JSONResponse(status_code=200,content=jsonable_encoder(data))
    
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={"success":False , "error":str(e)})    

@air_freight_router.post("/delete_air_freight_rate_surcharge")
def delete_air_freight_rate_surcharge_api(request:DeleteAirFreightRateSurchargeParams, resp:dict = Depends(authorize_token)):
    if resp['status_code']!=200:
        return JSONResponse(status_code=resp['status_code'],content=resp)
    if resp['isAuthorized']:
        request.performed_by_id=resp["setters"]["performed_by_id"]
    try:
        data=delete_air_freight_rate_surcharge(request.dict(exclude_none=True))
        return JSONResponse(status_code=200,content=jsonable_encoder(data))
    except HTTPException as e:
        raise 
    except Exception as e :
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500 , content={"success":False, "error":str(e)})

@air_freight_router.post("/delete_air_freight_rate_local")
def delete_air_freight_rate_local_api(request:DeleteAirFreightRateLocalParams, resp:dict = Depends(authorize_token)):
    if resp['status_code']!=200:
        return JSONResponse(status_code=resp['status_code'],content=resp)
    if resp['isAuthorized']:
        request.performed_by_id=resp["setters"]["performed_by_id"]
    try:
        data=delete_air_freight_rate_local(request.dict(exclude_none=True))
        return JSONResponse(status_code=200,content=jsonable_encoder(data))
    except HTTPException as e:
        raise 
    except Exception as e :
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500 , content={"success":False, "error":str(e)})
    

@extension_router.post("/create_draft_air_freight_rate")
def create_draft_air_freight_rate_api(request: CreateDraftAirFreightRateParams, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = create_draft_air_freight_rate(request.dict(exclude_none=False))
        return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })


@air_freight_router.post("/create_air_freight_rate_sheet")
def create_rate_sheets(request: CreateRateSheet, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        rate_sheet = create_rate_sheet(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(rate_sheet))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })



@air_freight_router.post("/update_air_freight_rate_sheet")
def update_rate_sheets(request: UpdateRateSheet, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]

    try:
        rate_sheet =update_rate_sheet(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=jsonable_encoder(rate_sheet))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })


@air_freight_router.get("/list_air_freight_rate_sheets")
def list_rates_sheets(
    filters: str = None,
    stats_required: bool = True,
    page: int = 1,
    page_limit: int = 10,
    sort_by: str = 'created_at',
    sort_type: str = 'desc',
    pagination_data_required:  bool = True,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        response = list_rate_sheets(
            filters, stats_required, page, page_limit,sort_by, sort_type, pagination_data_required
        )
        return JSONResponse(status_code=200, content=response)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })



@air_freight_router.get("/list_air_freight_rate_sheet_stats")
def list_rates_sheet_stat(
    filters: str = None,
    service_provider_id: str = None,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        response = list_rate_sheet_stats(
            filters, service_provider_id
        )
        return JSONResponse(status_code=200, content=response)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })