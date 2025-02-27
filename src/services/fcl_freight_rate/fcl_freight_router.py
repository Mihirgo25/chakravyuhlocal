from fastapi import APIRouter, Query, Depends, Request
from fastapi.responses import JSONResponse
from typing import Union, List
import json
import traceback
from libs.json_encoder import json_encoder
from params import *
from datetime import datetime, timedelta
from rms_utils.auth import authorize_token
import sentry_sdk
from fastapi import HTTPException
from pydantic import Json
from pydantic import Json



from services.fcl_freight_rate.interaction.update_schedule_in_fcl_freight_rate import update_schedule_in_fcl_freight_rate

from services.fcl_freight_rate.interaction.update_schedule_in_fcl_freight_rate import update_schedule_in_fcl_freight_rate
from libs.update_charges_yml import update_charges_yml
from services.fcl_freight_rate.interaction.create_fcl_freight_commodity_cluster import (
    create_fcl_freight_commodity_cluster,
)
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_local_agent import (
    create_fcl_freight_rate_local_agent,
)
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_not_available import (
    create_fcl_freight_rate_not_available,
)
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_task import (
    create_fcl_freight_rate_task,
)
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_request import (
    create_fcl_freight_rate_request,
)
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_local_request import (
    create_fcl_freight_rate_local_request,
)
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_feedback import (
    create_fcl_freight_rate_feedback,
)
from services.fcl_freight_rate.interaction.create_fcl_weight_slabs_configuration import (
    create_fcl_weight_slabs_configuration,
)
from services.fcl_freight_rate.interaction.get_fcl_freight_commodity_cluster import (
    get_fcl_freight_commodity_cluster,
)
from services.fcl_freight_rate.interaction.get_fcl_freight_rate import (
    get_fcl_freight_rate,
)
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_locals import (
    list_fcl_freight_rate_locals,
)
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_local_agents import (
    list_fcl_freight_rate_local_agents,
)
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_tasks import (
    list_fcl_freight_rate_tasks,
)
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_dislikes import (
    list_fcl_freight_rate_dislikes,
)
from services.fcl_freight_rate.interaction.get_fcl_freight_rate_local import (
    get_fcl_freight_rate_local,
)
from services.fcl_freight_rate.interaction.get_fcl_freight_local_rate_cards import (
    get_fcl_freight_local_rate_cards,
)
from services.fcl_freight_rate.interaction.get_fcl_freight_rate_cards import (
    get_fcl_freight_rate_cards,
)
from services.fcl_freight_rate.interaction.get_fcl_freight_rate_addition_frequency import (
    get_fcl_freight_rate_addition_frequency,
)
from services.fcl_freight_rate.interaction.get_fcl_freight_rate_suggestions import (
    get_fcl_freight_rate_suggestions,
)
from services.fcl_freight_rate.interaction.get_fcl_freight_rate_visibility import (
    get_fcl_freight_rate_visibility,
)
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_audits import (
    list_fcl_freight_rate_audits,
)
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_bulk_operations import (
    list_fcl_freight_rate_bulk_operations,
)
from services.fcl_freight_rate.interaction.list_dashboard_fcl_freight_rates import (
    list_dashboard_fcl_freight_rates,
)
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_requests import (
    list_fcl_freight_rate_requests,
)
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_local_requests import (
    list_fcl_freight_rate_local_requests,
)
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_feedbacks import (
    list_fcl_freight_rate_feedbacks,
)
from services.fcl_freight_rate.interaction.list_fcl_freight_commodity_clusters import (
    list_fcl_freight_commodity_clusters,
)
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_commodity_surcharges import (
    list_fcl_freight_rate_commodity_surcharges,
)
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_weight_limits import (
    list_fcl_freight_rate_weight_limits,
)
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_seasonal_surcharges import (
    list_fcl_freight_rate_seasonal_surcharges,
)
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_free_day_requests import (
    list_fcl_freight_rate_free_day_requests,
)
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_free_days import (
    list_fcl_freight_rate_free_days,
)
from services.fcl_freight_rate.interaction.list_fcl_weight_slabs_configuration import (
    list_fcl_weight_slabs_configuration,
)
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_local_suggestions import (
    list_fcl_freight_rate_local_suggestions,
)
from services.fcl_freight_rate.interaction.create_fcl_freight_rate import (
    create_fcl_freight_rate_data,
)
from services.fcl_freight_rate.interaction.delete_fcl_freight_rate import (
    delete_fcl_freight_rate,
)
from services.fcl_freight_rate.interaction.extend_create_fcl_freight_rate import (
    extend_create_fcl_freight_rate_data,
)
from services.fcl_freight_rate.interaction.update_fcl_freight_rate_extension_rule_set import (
    update_fcl_freight_rate_extension_rule_set_data,
)
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_extension_rule_sets import (
    list_fcl_freight_rate_extension_rule_set_data,
)
from services.fcl_freight_rate.interaction.update_fcl_freight_rate_task import (
    update_fcl_freight_rate_task_data,
)
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_extension_rule_set import (
    create_fcl_freight_rate_extension_rule_set_data,
)
from services.fcl_freight_rate.interaction.get_fcl_freight_rate_extension import (
    get_fcl_freight_rate_extension_data,
)
from services.fcl_freight_rate.interaction.get_fcl_freight_rate_weight_limit import (
    get_fcl_freight_rate_weight_limit,
)
from services.fcl_freight_rate.interaction.update_fcl_freight_rate import (
    update_fcl_freight_rate_data,
)
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_local import (
    create_fcl_freight_rate_local,
)
from services.fcl_freight_rate.interaction.update_fcl_freight_rate_local import (
    update_fcl_freight_rate_local,
)
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_weight_limit import (
    create_fcl_freight_rate_weight_limit,
)
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_free_day import (
    create_fcl_freight_rate_free_day,
)
from services.fcl_freight_rate.interaction.update_fcl_freight_rate_weight_limit import (
    update_fcl_freight_rate_weight_limit,
)
from services.fcl_freight_rate.interaction.get_fcl_freight_rate_free_day import (
    get_fcl_freight_rate_free_day,
)
from services.fcl_freight_rate.interaction.update_fcl_freight_rate_free_day import (
    update_fcl_freight_rate_free_day,
)
from services.fcl_freight_rate.interaction.get_fcl_freight_rate_stats import (
    get_fcl_freight_rate_stats,
)
from services.fcl_freight_rate.interaction.get_fcl_freight_rate_seasonal_surcharge import (
    get_fcl_freight_rate_seasonal_surcharge,
)
from services.fcl_freight_rate.interaction.get_fcl_freight_rate_commodity_surcharge import (
    get_fcl_freight_rate_commodity_surcharge,
)
from services.fcl_freight_rate.interaction.get_fcl_freight_commodity_cluster import (
    get_fcl_freight_commodity_cluster,
)
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_bulk_operation import (
    create_fcl_freight_rate_bulk_operation,
)
from services.fcl_freight_rate.interaction.create_critical_port_trend_index import (
    create_critical_port_trend_index,
)
from services.fcl_freight_rate.interaction.delete_fcl_freight_rate_request import (
    delete_fcl_freight_rate_request,
)
from services.fcl_freight_rate.interaction.delete_fcl_freight_rate_feedback import (
    delete_fcl_freight_rate_feedback,
)
from services.fcl_freight_rate.interaction.delete_fcl_freight_rate_local_request import (
    delete_fcl_freight_rate_local_request,
)
from services.fcl_freight_rate.interaction.delete_fcl_freight_rate_local import (
    delete_fcl_freight_rate_local,
)
from services.fcl_freight_rate.interaction.delete_fcl_freight_rate_free_day_request import (
    delete_fcl_freight_rate_free_day_request,
)
from services.fcl_freight_rate.interaction.update_fcl_freight_rate_local_agent import (
    update_fcl_freight_rate_local_agent,
)
from services.fcl_freight_rate.interaction.update_fcl_weight_slabs_configuration import (
    update_fcl_weight_slabs_configuration,
)
from services.fcl_freight_rate.interaction.update_fcl_freight_rate_platform_prices import (
    update_fcl_freight_rate_platform_prices,
)
from services.fcl_freight_rate.interaction.update_fcl_freight_commodity_cluster import (
    update_fcl_freight_commodity_cluster,
)
from services.fcl_freight_rate.interaction.update_fcl_freight_rate_commodity_surcharge import (
    update_fcl_freight_rate_commodity_surcharge,
)
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_free_day_request import (
    create_fcl_freight_rate_free_day_request,
)
from services.fcl_freight_rate.interaction.list_fcl_freight_rates import (
    list_fcl_freight_rates,
)
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_commodity_surcharge import (
    create_fcl_freight_rate_commodity_surcharge,
)
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_seasonal_surcharge import (
    create_fcl_freight_rate_seasonal_surcharge,
)
from services.fcl_freight_rate.interaction.get_eligible_fcl_freight_rate_free_day import (
    get_eligible_fcl_freight_rate_free_day,
)
from services.fcl_freight_rate.interaction.get_fcl_freight_weight_slabs_for_rates import (
    get_fcl_freight_weight_slabs_for_rates,
)
from services.fcl_freight_rate.interaction.get_fcl_freight_rate_properties import (
    get_fcl_freight_rate_properties,
)
from services.fcl_freight_rate.interaction.update_fcl_freight_rate_properties import (
    update_fcl_freight_rate_properties,
)
from services.fcl_freight_rate.interaction.get_suggested_cogo_assured_fcl_freight_rates import (
    get_suggested_cogo_assured_fcl_freight_rates,
)
from services.rate_sheet.interactions.create_rate_sheet import create_rate_sheet
from services.rate_sheet.interactions.update_rate_sheet import update_rate_sheet
from services.rate_sheet.interactions.list_rate_sheets import list_rate_sheets
from services.rate_sheet.interactions.list_rate_sheet_stats import list_rate_sheet_stats
from services.fcl_freight_rate.interaction.get_fcl_freight_rate_for_lcl import (
    get_fcl_freight_rate_for_lcl,
)
from configs.fcl_freight_rate_constants import (
    COGO_ASSURED_SERVICE_PROVIDER_ID,
    DEFAULT_PROCURED_BY_ID,
    COGO_ASSURED_SHIPPING_LINE_ID,
)
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_deviations import (
    list_fcl_freight_rate_deviations,
)
from services.fcl_freight_rate.interaction.create_fcl_freight_location_cluster import (
    create_fcl_freight_location_cluster,
)
from services.fcl_freight_rate.interaction.get_fcl_freight_rate_job_stats import (
    get_fcl_freight_rate_job_stats,
)
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_jobs import (
    list_fcl_freight_rate_jobs,
)
from services.fcl_freight_rate.interaction.delete_fcl_freight_rate_job import (
    delete_fcl_freight_rate_job,
)
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_job import (
    create_fcl_freight_rate_job,
)

from services.ltl_freight_rate.ltl_params import (
    CreateLtlFreightRateJob,
    DeleteLtlFreightRateJob,
    UpdateLtlFreightRateJobOnRateAddition,
)

from services.ltl_freight_rate.interactions.create_ltl_freight_rate_job import (
    create_ltl_freight_rate_job,
)
from services.ltl_freight_rate.interactions.delete_ltl_freight_rate_job import (
    delete_ltl_freight_rate_job,
)
from services.ltl_freight_rate.interactions.list_ltl_freight_rate_jobs import (
    list_ltl_freight_rate_jobs,
)
from services.ltl_freight_rate.interactions.get_ltl_freight_rate_job_stats import (
    get_ltl_freight_rate_job_stats,
)

from services.lcl_customs_rate.lcl_customs_params import (
    CreateLclCustomsRateJob,
    DeleteLclCustomsRateJob,
    UpdateLclCustomsRateJobOnRateAddition,
)

from services.lcl_customs_rate.interactions.create_lcl_customs_rate_job import (
    create_lcl_customs_rate_job,
)
from services.lcl_customs_rate.interactions.delete_lcl_customs_rate_job import (
    delete_lcl_customs_rate_job,
)
from services.lcl_customs_rate.interactions.list_lcl_customs_rate_jobs import (
    list_lcl_customs_rate_jobs,
)
from services.lcl_customs_rate.interactions.get_lcl_customs_rate_job_stats import (
    get_lcl_customs_rate_job_stats,
)

from services.lcl_freight_rate.lcl_params import (
    CreateLclFreightRateJob,
    DeleteLclFreightRateJob,
    UpdateLclFreightRateJobOnRateAddition,
)

from services.lcl_freight_rate.interactions.create_lcl_freight_rate_job import (
    create_lcl_freight_rate_job,
)
from services.lcl_freight_rate.interactions.delete_lcl_freight_rate_job import (
    delete_lcl_freight_rate_job,
)
from services.lcl_freight_rate.interactions.list_lcl_freight_rate_jobs import (
    list_lcl_freight_rate_jobs,
)
from services.lcl_freight_rate.interactions.get_lcl_freight_rate_job_stats import (
    get_lcl_freight_rate_job_stats,
)
from services.fcl_freight_rate.interaction.update_fcl_freight_rate_job import (
    update_fcl_freight_rate_job,
)
from services.ltl_freight_rate.ltl_params import UpdateLtlFreightRateJob
from services.ltl_freight_rate.interactions.update_ltl_freight_rate_job import (
    update_ltl_freight_rate_job,
)
from services.lcl_freight_rate.lcl_params import UpdateLclFreightRateJob
from services.lcl_freight_rate.interactions.update_lcl_freight_rate_job import (
    update_lcl_freight_rate_job,
)
from services.lcl_customs_rate.lcl_customs_params import UpdateLclCustomsRateJob
from services.lcl_customs_rate.interactions.update_lcl_customs_rate_job import (
    update_lcl_customs_rate_job,
)

from services.lcl_customs_rate.workers.update_lcl_customs_rate_job_on_rate_addition import (
    update_lcl_customs_rate_job_on_rate_addition,
)
from services.lcl_freight_rate.workers.update_lcl_freight_rate_job_on_rate_addition import (
    update_lcl_freight_rate_job_on_rate_addition,
)
from services.ltl_freight_rate.workers.update_ltl_freight_rate_job_on_rate_addition import (
    update_ltl_freight_rate_job_on_rate_addition,
)
from services.fcl_freight_rate.interaction.get_fcl_freight_rate_cards_with_schedules import get_fcl_freight_rate_cards_with_schedules
from services.fcl_freight_rate.interaction.get_fcl_freight_rate_cards_with_schedules import get_fcl_freight_rate_cards_with_schedules
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_local_job import (
    create_fcl_freight_rate_local_job,
)
from services.fcl_freight_rate.interaction.delete_fcl_freight_rate_local_job import (
    delete_fcl_freight_rate_local_job,
)
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_local_jobs import (
    list_fcl_freight_rate_local_jobs,
)
from services.fcl_freight_rate.interaction.get_fcl_freight_rate_local_job_stats import (
    get_fcl_freight_rate_local_job_stats,
)
from services.fcl_freight_rate.interaction.update_fcl_freight_rate_local_job import (
    update_fcl_freight_rate_local_job,
)
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_local_feedbacks import (
    list_fcl_freight_rate_local_feedbacks,
)
from services.fcl_freight_rate.interaction.delete_fcl_freight_rate_local_feedback import (
    delete_fcl_freight_rate_local_feedback,
)
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_local_feedback import (
    create_fcl_freight_rate_local_feedback,
)

from libs.rate_limiter import rate_limiter
from configs.env import DEFAULT_USER_ID

fcl_freight_router = APIRouter()


@fcl_freight_router.post("/create_fcl_freight_commodity_cluster")
def create_fcl_freight_commodity_cluster_data(
    request: CreateFclFreightCommodityCluster, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = create_fcl_freight_commodity_cluster(request.dict(exclude_none=False))
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/create_fcl_freight_rate_commodity_surcharge")
def create_fcl_freight_rate_commodity_surcharge_data(
    request: CreateFclFreightRateCommoditySurcharge,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        rate = create_fcl_freight_rate_commodity_surcharge(
            request.dict(exclude_none=True)
        )
        return JSONResponse(status_code=200, content=json_encoder(rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/create_fcl_freight_rate_local_agent")
def create_fcl_freight_rate_local_agent_data(
    request: CreateFclFreightRateLocalAgent, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = create_fcl_freight_rate_local_agent(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/create_fcl_freight_rate")
def create_fcl_freight_rate_func(
    request: PostFclFreightRate, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    if request.rate_type == "cogo_assured":
        request.shipping_line_id = COGO_ASSURED_SHIPPING_LINE_ID
        request.service_provider_id = COGO_ASSURED_SERVICE_PROVIDER_ID
        request.sourced_by_id = DEFAULT_USER_ID
        request.procured_by_id = request.performed_by_id

    not_available_params = []
    if not request.shipping_line_id:
        not_available_params.append("Shipping line")

    if not request.sourced_by_id:
        not_available_params.append("Sourced by")

    if not request.service_provider_id:
        not_available_params.append("Service provider")

    if (
        not request.shipping_line_id
        or not request.sourced_by_id
        or not request.service_provider_id
    ):
        details = " ".join(not_available_params) + " not present"
        raise HTTPException(status_code=400, detail=details)

    try:
        rate = create_fcl_freight_rate_data(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(rate))
    except HTTPException as e:
        raise
    except Exception as e:
        # raise
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "traceback": traceback.print_exc(),
            },
        )


@fcl_freight_router.post("/create_fcl_freight_rate_feedback")
def create_fcl_freight_rate_feedback_data(
    request: CreateFclFreightRateFeedback, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        rate_id = create_fcl_freight_rate_feedback(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(rate_id))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/create_fcl_freight_rate_not_available")
def create_fcl_freight_rate_not_available_data(
    request: CreateFclFreightRateNotAvailable, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    data = create_fcl_freight_rate_not_available(request)
    if data:
        try:
            return JSONResponse(status_code=200, content={"success": True})
        except HTTPException as e:
            raise
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return JSONResponse(
                status_code=500, content={"success": False, "error": str(e)}
            )
    return JSONResponse(
        status_code=400, content={"success": False, "error": "No data available"}
    )


@fcl_freight_router.post("/create_fcl_freight_rate_local")
def create_fcl_freight_rate_local_data(
    request: PostFclFreightRateLocal, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = create_fcl_freight_rate_local(request.dict(exclude_none=False))
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/create_fcl_freight_rate_task")
def create_fcl_freight_rate_task_data(
    request: CreateFclFreightRateTask, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = create_fcl_freight_rate_task(request.dict(exclude_none=False))
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        traceback.print_exc()
        print(request.dict(exclude_none=False))
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/create_fcl_freight_rate_request")
def create_fcl_freight_rate_request_data(
    request: CreateFclFreightRateRequest, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = create_fcl_freight_rate_request(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/create_fcl_freight_rate_local_request")
def create_fcl_freight_rate_local_request_data(
    request: CreateFclFreightRateLocalRequest, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = create_fcl_freight_rate_local_request(request)
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/create_fcl_weight_slabs_configuration")
def create_fcl_weight_slabs_configuration_data(
    request: CreateFclWeightSlabsConfiguration, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = create_fcl_weight_slabs_configuration(request.dict(exclude_none=False))
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/get_fcl_freight_rate")
def get_fcl_freight_rate_data(
    id: str = None,
    origin_port_id: str = None,
    origin_main_port_id: str = None,
    destination_port_id: str = None,
    destination_main_port_id: str = None,
    container_size: str = None,
    container_type: str = None,
    commodity: str = None,
    shipping_line_id: str = None,
    service_provider_id: str = None,
    importer_exporter_id: str = None,
    cogo_entity_id: str = None,
    rate_type: str = "market_place",
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    request = {
        "id": id,
        "origin_port_id": origin_port_id,
        "origin_main_port_id": origin_main_port_id,
        "destination_port_id": destination_port_id,
        "destination_main_port_id": destination_main_port_id,
        "container_size": container_size,
        "container_type": container_type,
        "commodity": commodity,
        "shipping_line_id": shipping_line_id,
        "service_provider_id": service_provider_id,
        "importer_exporter_id": importer_exporter_id,
        "cogo_entity_id": cogo_entity_id,
        "rate_type": rate_type,
    }

    try:
        data = get_fcl_freight_rate(request)
        data = json_encoder(data)
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/get_fcl_freight_rate_for_lcl")
def get_fcl_freight_rate_for_lcl_func(
    origin_port_id: str = None,
    origin_main_port_id: str = None,
    destination_port_id: str = None,
    destination_main_port_id: str = None,
    container_size: str = None,
    container_type: str = None,
    commodity: str = None,
    shipping_line_id: str = None,
    service_provider_id: str = None,
    importer_exporter_id: str = None,
    origin_country_id: str = None,
    destination_country_id: str = None,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        request = {
            "origin_port_id": origin_port_id,
            "origin_main_port_id": origin_main_port_id,
            "destination_port_id": destination_port_id,
            "destination_main_port_id": destination_main_port_id,
            "origin_country_id": origin_country_id,
            "destination_country_id": destination_country_id,
            "container_size": container_size,
            "container_type": container_type,
            "commodity": commodity,
            "shipping_line_id": shipping_line_id,
            "service_provider_id": service_provider_id,
            "importer_exporter_id": importer_exporter_id,
        }

        data = get_fcl_freight_rate_for_lcl(request)
        data = json_encoder(data)
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/get_fcl_freight_rate_local")
def get_fcl_freight_local_data(
    id: str = None,
    port_id: str = None,
    main_port_id: str = None,
    trade_type: str = None,
    container_size: str = None,
    container_type: str = None,
    commodity: str = None,
    rate_type: str = "market_place",
    shipping_line_id: str = None,
    service_provider_id: str = None,
    get_parsed_values: bool = False,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    request = {
        "id": id,
        "port_id": port_id,
        "main_port_id": main_port_id,
        "trade_type": trade_type,
        "container_size": container_size,
        "container_type": container_type,
        "commodity": commodity,
        "rate_type": rate_type,
        "shipping_line_id": shipping_line_id,
        "service_provider_id": service_provider_id,
        "get_parsed_values": get_parsed_values,
    }

    try:
        data = get_fcl_freight_rate_local(request)
        data = json_encoder(data)
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/get_fcl_freight_local_rate_cards")
def get_fcl_freight_local_rate_cards_data(
    trade_type: str,
    port_id: str,
    country_id: str,
    container_size: str,
    container_type: str,
    containers_count: int,
    bls_count: int,
    terminal_id: str = None,
    commodity: str = None,
    shipping_line_id: str = None,
    service_provider_id: str = None,
    rates: List[str] | None = Query(None),
    include_confirmed_inventory_rates: bool = False,
    additional_services: List[str] | None = Query(None),
    include_destination_dpd: bool = False,
    cargo_weight_per_container: int = 0,
    primary_service_object: str = None,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    if (
        additional_services
        and len(additional_services) == 1
        and not additional_services[0]
    ):
        additional_services = []
    if rates and len(rates) == 1 and not rates[0]:
        rates = []

    request = {
        "trade_type": trade_type,
        "port_id": port_id,
        "terminal_id": terminal_id,
        "country_id": country_id,
        "container_size": container_size,
        "container_type": container_type,
        "containers_count": containers_count,
        "bls_count": bls_count,
        "commodity": commodity,
        "shipping_line_id": shipping_line_id or None,
        "service_provider_id": service_provider_id or None,
        "rates": rates or [],
        "cargo_weight_per_container": cargo_weight_per_container,
        "include_destination_dpd": include_destination_dpd,
        "additional_services": additional_services or [],
        "include_confirmed_inventory_rates": include_confirmed_inventory_rates,
        "primary_service_object": primary_service_object,
    }

    try:
        data = get_fcl_freight_local_rate_cards(request)
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/get_fcl_freight_rate_cards")
def get_fcl_freight_rate_cards_data(
    origin_port_id: str,
    origin_country_id: str,
    destination_port_id: str,
    destination_country_id: str,
    container_size: str,
    container_type: str,
    containers_count: int,
    validity_start: str,
    validity_end: str,
    trade_type: str = None,
    include_destination_local: bool = True,
    include_origin_local: bool = True,
    cogo_entity_id: str = None,
    importer_exporter_id: str = None,
    bls_count: int = 1,
    commodity: str = None,
    shipping_line_id: str = None,
    service_provider_id: str = None,
    terminal_id: str = None,
    include_confirmed_inventory_rates: bool = False,
    additional_services: str = None,
    ignore_omp_dmp_sl_sps: str = None,
    include_destination_dpd: bool = False,
    cargo_weight_per_container: int = 0,
    search_source: str = "platform",
    resp: dict = Depends(authorize_token),
):
    try:
        validity_start = datetime.fromisoformat(validity_start).date()
        validity_end = datetime.fromisoformat(validity_end).date()
    except:
        validity_start = datetime.now().date()
        validity_end = (datetime.now() + timedelta(days=30)).date()
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    if additional_services:
        additional_services = json.loads(additional_services)
    else:
        additional_services = []
    if ignore_omp_dmp_sl_sps:
        ignore_omp_dmp_sl_sps = json.loads(ignore_omp_dmp_sl_sps)
    else:
        ignore_omp_dmp_sl_sps = []
    if not importer_exporter_id:
        importer_exporter_id = None
    # validity_start = datetime.strptime(validity_start,'%Y-%m-%d')
    # validity_end = datetime.strptime(validity_end,'%Y-%m-%d')
    request = {
        "origin_port_id": origin_port_id,
        "origin_country_id": origin_country_id,
        "destination_port_id": destination_port_id,
        "destination_country_id": destination_country_id,
        "container_size": container_size,
        "container_type": container_type,
        "containers_count": containers_count,
        "bls_count": bls_count,
        "commodity": commodity,
        "importer_exporter_id": importer_exporter_id,
        "trade_type": trade_type,
        "shipping_line_id": shipping_line_id,
        "service_provider_id": service_provider_id,
        "terminal_id": terminal_id,
        "validity_start": validity_start,
        "validity_end": validity_end,
        "include_origin_local": include_origin_local,
        "include_destination_local": include_destination_local,
        "cargo_weight_per_container": cargo_weight_per_container,
        "include_destination_dpd": include_destination_dpd,
        "additional_services": additional_services,
        "include_confirmed_inventory_rates": include_confirmed_inventory_rates,
        "ignore_omp_dmp_sl_sps": ignore_omp_dmp_sl_sps,
        "cogo_entity_id": cogo_entity_id,
        "search_source": search_source,
    }

    try:
        data = get_fcl_freight_rate_cards(request)
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/get_fcl_freight_rate_addition_frequency")
def get_fcl_freight_rate_addition_frequency_data(
    group_by: str,
    filters: str = None,
    sort_type: str = "desc",
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = get_fcl_freight_rate_addition_frequency(group_by, filters, sort_type)
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/get_fcl_freight_rate_suggestions")
def get_fcl_freight_rate_suggestions_data(
    validity_start: str,
    validity_end: str,
    searched_origin_port_id: str = None,
    searched_destination_port_id: str = None,
    filters: str = None,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = get_fcl_freight_rate_suggestions(
            validity_start,
            validity_end,
            searched_origin_port_id,
            searched_destination_port_id,
            filters,
        )
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/get_fcl_freight_rate_visibility")
def get_fcl_freight_rate_visibility_data(
    service_provider_id: str,
    origin_port_id: str = None,
    destination_port_id: str = None,
    from_date: datetime = None,
    to_date: datetime = None,
    rate_id: str = None,
    shipping_line_id: str = None,
    container_size: str = None,
    container_type: str = None,
    commodity: str = None,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    request = {
        "service_provider_id": service_provider_id,
        "origin_port_id": origin_port_id,
        "destination_port_id": destination_port_id,
        "from_date": from_date,
        "to_date": to_date,
        "rate_id": rate_id,
        "shipping_line_id": shipping_line_id,
        "container_size": container_size,
        "container_type": container_type,
        "commodity": commodity,
    }
    try:
        data = get_fcl_freight_rate_visibility(request)
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/list_dashboard_fcl_freight_rates")
def list_dashboard_fcl_freight_rates_data(resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = list_dashboard_fcl_freight_rates()
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/list_fcl_freight_rate_audits")
def list_fcl_freight_audits_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    sort_by: str = "created_at",
    sort_type: str = "asc",
    pagination_data_required: bool = False,
    user_data_required: bool = False,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        data = list_fcl_freight_rate_audits(
            filters,
            page_limit,
            page,
            sort_by,
            sort_type,
            pagination_data_required,
            user_data_required,
        )
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/list_fcl_freight_rate_bulk_operations")
def list_fcl_freight_rate_bulk_operations_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = list_fcl_freight_rate_bulk_operations(filters, page_limit, page)
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/list_fcl_freight_rate_free_day_requests")
def list_fcl_freight_rate_free_day_requests_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    is_stats_required: bool = True,
    performed_by_id: str = None,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        data = list_fcl_freight_rate_free_day_requests(
            filters, page_limit, page, is_stats_required, performed_by_id
        )
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/list_fcl_freight_rates")
def list_fcl_freight_rates_data(
    filters: str = None,
    includes: str = None,
    page_limit: int = 10,
    page: int = 1,
    sort_by: str = "updated_at",
    sort_type: str = "desc",
    return_query: bool = False,
    expired_rates_required: bool = False,
    return_count: bool = False,
    is_line_items_required: bool = False,
    pagination_data_required: bool = False,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = list_fcl_freight_rates(
            filters,
            page_limit,
            page,
            sort_by,
            sort_type,
            return_query,
            expired_rates_required,
            return_count,
            is_line_items_required,
            includes,
            pagination_data_required,
        )
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/list_fcl_freight_rate_locals")
def list_fcl_freight_rate_locals_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    sort_by: str = "updated_at",
    sort_type: str = "desc",
    return_query: bool = False,
    get_count: bool = False,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = list_fcl_freight_rate_locals(
            filters, page_limit, page, sort_by, sort_type, return_query, get_count
        )
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/list_fcl_freight_rate_local_agents")
def list_fcl_freight_rate_local_agent_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    sort_by: str = "updated_at",
    sort_type: str = "desc",
    pagination_data_required: bool = True,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        data = list_fcl_freight_rate_local_agents(
            filters, page_limit, page, sort_by, sort_type, pagination_data_required
        )
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/list_fcl_freight_rate_tasks")
def list_fcl_freight_rate_tasks_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    sort_by: str = "created_at",
    sort_type: str = "desc",
    stats_required: bool = True,
    pagination_data_required: bool = True,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = list_fcl_freight_rate_tasks(
            filters,
            page_limit,
            page,
            sort_by,
            sort_type,
            stats_required,
            pagination_data_required,
        )
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/list_fcl_freight_rate_requests")
def list_fcl_freight_rate_requests_data(
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
        data = list_fcl_freight_rate_requests(
            filters, page_limit, page, performed_by_id, is_stats_required
        )
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/list_fcl_freight_rate_local_requests")
def list_fcl_freight_rate_local_requests_data(
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
        data = list_fcl_freight_rate_local_requests(
            filters, page_limit, page, is_stats_required, performed_by_id
        )
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/list_fcl_freight_rate_seasonal_surcharges")
def list_fcl_freight_rate_seasonal_surcharges_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    pagination_data_required: bool = True,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        data = list_fcl_freight_rate_seasonal_surcharges(
            filters, page_limit, page, pagination_data_required
        )
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/list_fcl_freight_rate_feedbacks")
def list_fcl_freight_rate_feedbacks_data(
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
        data = list_fcl_freight_rate_feedbacks(
            filters,
            spot_search_details_required,
            page_limit,
            page,
            performed_by_id,
            is_stats_required,
            booking_details_required,
        )
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/list_fcl_freight_commodity_clusters")
def list_fcl_freight_rate_commodity_clusters_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    pagination_data_required: bool = True,
    sort_by: str = "updated_at",
    sort_type: str = "desc",
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        data = list_fcl_freight_commodity_clusters(
            filters, page_limit, page, pagination_data_required, sort_by, sort_type
        )
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/list_fcl_freight_rate_commodity_surcharges")
def list_fcl_freight_rate_commodity_surcharges_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    pagination_data_required: bool = True,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        data = list_fcl_freight_rate_commodity_surcharges(
            filters, page_limit, page, pagination_data_required
        )
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/list_fcl_freight_rate_dislikes")
def list_fcl_freight_rate_dislikes_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        data = list_fcl_freight_rate_dislikes(filters, page_limit, page)
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/list_fcl_freight_rate_local_suggestions")
def list_fcl_freight_local_suggestions_data(
    service_provider_id: str,
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    sort_by: str = "updated_at",
    sort_type: str = "desc",
    pagination_data_required: bool = True,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)
    try:
        data = list_fcl_freight_rate_local_suggestions(
            service_provider_id,
            filters,
            page_limit,
            page,
            sort_by,
            sort_type,
            pagination_data_required,
        )
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/list_fcl_freight_rate_free_days")
def list_fcl_freight_rate_free_days_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    pagination_data_required: bool = True,
    return_query: bool = False,
    includes: str = None,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        data = list_fcl_freight_rate_free_days(
            filters, page_limit, page, pagination_data_required, return_query, includes
        )
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/list_public_fcl_freight_rate_free_days")
@rate_limiter.add(max_requests=10, time_window=3600)
def list_public_fcl_freight_rate_data(
    request: Request,
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    pagination_data_required: bool = False,
    return_query: bool = False,
    includes: str = None,
):
    try:
        data = list_fcl_freight_rate_free_days(
            filters, page_limit, page, pagination_data_required, return_query, includes
        )
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/list_fcl_freight_rate_weight_limits")
def list_fcl_freight_rate_weight_limits_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    pagination_data_required: bool = True,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        data = list_fcl_freight_rate_weight_limits(
            filters, page_limit, page, pagination_data_required
        )
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/list_fcl_weight_slabs_configuration")
def list_fcl_weight_slabs_configuration_data(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    pagination_data_required: bool = True,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        data = list_fcl_weight_slabs_configuration(
            filters, page_limit, page, pagination_data_required
        )
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/update_fcl_freight_rate")
def update_fcl_freight_rate(
    request: UpdateFclFreightRate, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    if request.rate_type == "cogo_assured":
        request.sourced_by_id = request.performed_by_id
        request.procured_by_id = DEFAULT_PROCURED_BY_ID
    try:
        data = update_fcl_freight_rate_data(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/update_fcl_freight_rate_local")
def update_fcl_freight_rate_local_data(
    request: UpdateFclFreightRateLocal, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = update_fcl_freight_rate_local(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/update_fcl_freight_rate_properties")
def update_fcl_freight_rate_properties_data(
    request: UpdateRateProperties, resp: dict = Depends(authorize_token)
):
    try:
        data = update_fcl_freight_rate_properties(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/update_fcl_freight_rate_local_agent")
def update_fcl_freight_rate_local_agent_data(
    request: UpdateFclFreightRateLocalAgent, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = update_fcl_freight_rate_local_agent(request.__dict__)
        data = json_encoder(data)
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/update_fcl_weight_slabs_configuration")
def update_fcl_weight_slabs_configuration_data(
    request: UpdateFclWeightSlabsConfiguration, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = update_fcl_weight_slabs_configuration(request.dict(exclude_none=True))
        data = json_encoder(data)
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/update_fcl_freight_rate_platform_prices")
def update_fcl_freight_rate_platform_prices_data(
    request: UpdateFclFreightRatePlatformPrices, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = update_fcl_freight_rate_platform_prices(request.dict(exclude_none=False))
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/delete_fcl_freight_rate")
def delete_fcl_freight_rates(
    request: DeleteFclFreightRate, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    if request.rate_type == "cogo_assured":
        request.sourced_by_id = DEFAULT_USER_ID
        request.procured_by_id = DEFAULT_PROCURED_BY_ID
    try:
        delete_rate = delete_fcl_freight_rate(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(delete_rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/create_fcl_freight_rate_extension_rule_set")
def create_fcl_freight_rate_extension_rule_set(
    request: PostFclFreightRateExtensionRuleSet, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = create_fcl_freight_rate_extension_rule_set_data(
            request.dict(exclude_none=True)
        )
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/extend_create_fcl_freight_rate")
def extend_create_fcl_freight_rate(
    request: ExtendCreateFclFreightRate, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = extend_create_fcl_freight_rate_data(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/update_fcl_freight_rate_extension_rule_set")
def update_fcl_freight_rate_extension_rule_set(
    request: UpdateFclFreightRateExtensionRuleSet, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]

    try:
        data = update_fcl_freight_rate_extension_rule_set_data(
            request.dict(exclude_none=True)
        )
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/list_fcl_freight_rate_extension_rule_sets")
def list_fcl_freight_rate_extension_rule_set(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    sort_by: str = "updated_at",
    sort_type: str = "desc",
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        data = list_fcl_freight_rate_extension_rule_set_data(
            filters, page_limit, page, sort_by, sort_type
        )
        data = json_encoder(data)
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/get_fcl_freight_rate_extension")
def get_fcl_freight_rate_extension(
    service_provider_id: str,
    shipping_line_id: str,
    origin_port_id: str,
    destination_port_id: str,
    commodity: str,
    container_size: str,
    container_type: str = None,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        data = get_fcl_freight_rate_extension_data(
            service_provider_id,
            shipping_line_id,
            origin_port_id,
            destination_port_id,
            commodity,
            container_size,
            container_type,
        )
        data = json_encoder(data)
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/update_fcl_freight_rate_task")
def update_fcl_freight_rate_task(
    request: UpdateFclFreightRateTask, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        return JSONResponse(
            status_code=200,
            content=update_fcl_freight_rate_task_data(request.dict(exclude_none=False)),
        )
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/delete_fcl_freight_rate_request")
def delete_fcl_freight_rates_request(
    request: DeleteFclFreightRateRequest, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        delete_rate = delete_fcl_freight_rate_request(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(delete_rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/delete_fcl_freight_rate_feedback")
def delete_fcl_freight_rates_feedback(
    request: DeleteFclFreightRateFeedback, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        delete_rate = delete_fcl_freight_rate_feedback(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(delete_rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/delete_fcl_freight_rate_local_request")
def delete_fcl_freight_rates_local_request(
    request: DeleteFclFreightRateLocalRequest, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        delete_rate = delete_fcl_freight_rate_local_request(
            request.dict(exclude_none=True)
        )
        return JSONResponse(status_code=200, content=json_encoder(delete_rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/delete_fcl_freight_rate_local")
def delete_fcl_freight_rates_local(
    request: DeleteFclFreightRateLocal, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        delete_rate = delete_fcl_freight_rate_local(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(delete_rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/delete_fcl_freight_rate_free_day_request")
def delete_fcl_freight_rates_free_day_request(
    request: DeleteFclFreightRateFreeDayRequest, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        delete_rate = delete_fcl_freight_rate_free_day_request(
            request.dict(exclude_none=True)
        )
        return JSONResponse(status_code=200, content=json_encoder(delete_rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/create_fcl_freight_rate_weight_limit")
def create_fcl_freight_rate_weight_limit_data(
    request: CreateFclFreightRateWeightLimit, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = create_fcl_freight_rate_weight_limit(request.dict(exclude_none=False))
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/get_fcl_freight_rate_weight_limit")
def get_fcl_freight_rate_weight_limit_data(
    origin_location_id: str = None,
    destination_location_id: str = None,
    container_size: str = None,
    container_type: str = None,
    shipping_line_id: str = None,
    service_provider_id: str = None,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    request = {
        "origin_location_id": origin_location_id,
        "destination_location_id": destination_location_id,
        "container_size": container_size,
        "container_type": container_type,
        "shipping_line_id": shipping_line_id,
        "service_provider_id": service_provider_id,
    }
    try:
        data = get_fcl_freight_rate_weight_limit(request)
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/update_fcl_freight_rate_weight_limit")
def update_fcl_freight_rate_weight_limit_data(
    request: UpdateFclFreightRateWeightLimit, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = update_fcl_freight_rate_weight_limit(request.dict(exclude_none=False))
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/create_fcl_freight_rate_free_day")
def create_fcl_freight_rate_free_day_data(
    request: CreateFclFreightRateFreeDay, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = create_fcl_freight_rate_free_day(request.dict(exclude_none=False))
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/get_fcl_freight_rate_free_day")
def get_fcl_freight_rate_free_day_data(
    location_id: str = None,
    trade_type: str = None,
    free_days_type: str = None,
    container_size: str = None,
    container_type: str = None,
    shipping_line_id: str = None,
    service_provider_id: str = None,
    importer_exporter_id: str = None,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    request = {
        "location_id": location_id,
        "trade_type": trade_type,
        "free_days_type": free_days_type,
        "container_size": container_size,
        "container_type": container_type,
        "shipping_line_id": shipping_line_id,
        "service_provider_id": service_provider_id,
        "importer_exporter_id": importer_exporter_id,
    }
    try:
        data = get_fcl_freight_rate_free_day(request)
        data = json_encoder(data)
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/update_fcl_freight_rate_free_day")
def update_fcl_freight_rate_free_day_data(
    request: UpdateFclFreightRateFreeDay, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = update_fcl_freight_rate_free_day(request.dict(exclude_none=False))
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/get_fcl_freight_rate_stats")
def get_fcl_freight_rate_stats_data(
    validity_start: datetime,
    validity_end: datetime,
    stats_types: str = None,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    request = {
        "validity_start": validity_start,
        "validity_end": validity_end,
        "stats_types": json.loads(stats_types),
    }
    try:
        data = get_fcl_freight_rate_stats(request)
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/get_fcl_freight_rate_properties")
def get_fcl_freight_rate_properties_data(rate_id: str = None):
    try:
        data = get_fcl_freight_rate_properties(rate_id)
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/get_fcl_freight_rate_seasonal_surcharge")
def get_fcl_freight_rate_seasonal_surcharge_data(
    origin_location_id: str = None,
    destination_location_id: str = None,
    container_size: str = None,
    container_type: str = None,
    code: str = None,
    shipping_line_id: str = None,
    service_provider_id: str = None,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    request = {
        "origin_location_id": origin_location_id,
        "destination_location_id": destination_location_id,
        "container_size": container_size,
        "container_type": container_type,
        "code": code,
        "shipping_line_id": shipping_line_id,
        "service_provider_id": service_provider_id,
    }
    try:
        data = get_fcl_freight_rate_seasonal_surcharge(request)
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/get_fcl_freight_rate_commodity_surcharge")
def get_fcl_freight_rate_commodity_surcharge_data(
    origin_location_id: str = None,
    destination_location_id: str = None,
    container_size: str = None,
    container_type: str = None,
    commodity: str = None,
    shipping_line_id: str = None,
    service_provider_id: str = None,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    request = {
        "origin_location_id": origin_location_id,
        "destination_location_id": destination_location_id,
        "container_size": container_size,
        "container_type": container_type,
        "commodity": commodity,
        "shipping_line_id": shipping_line_id,
        "service_provider_id": service_provider_id,
    }
    try:
        data = get_fcl_freight_rate_commodity_surcharge(request)
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/get_fcl_freight_commodity_cluster")
def get_fcl_freight_commodity_cluster_data(
    id: str, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        data = get_fcl_freight_commodity_cluster(id)
        data = json_encoder(data)
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/update_fcl_freight_commodity_cluster")
def update_fcl_freight_commodity_cluster_data(
    request: UpdateFclFreightCommodityCluster, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = update_fcl_freight_commodity_cluster(request)
        data = json_encoder(data)
        return JSONResponse(status_code=200, content=data)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/update_fcl_freight_commodity_surcharge")
def update_fcl_freight_commodity_surcharge_data(
    request: UpdateFclFreightRateCommoditySurcharge,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = update_fcl_freight_rate_commodity_surcharge(
            request.dict(exclude_none=False)
        )
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/create_fcl_freight_rate_seasonal_surcharge")
def create_fcl_freight_rate_seasonal_surcharge_data(
    request: CreateFclFreightSeasonalSurcharge, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = create_fcl_freight_rate_seasonal_surcharge(
            request.dict(exclude_none=False)
        )
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/create_fcl_freight_rate_bulk_operation")
def create_fcl_freight_rate_bulk_operation_data(
    request: CreateBulkOperation, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data=create_fcl_freight_rate_bulk_operation(request.dict(exclude_none=True))
        return JSONResponse(content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })


@fcl_freight_router.post("/create_fcl_freight_rate_free_day_request")
def create_fcl_freight_rate_free_day_requests(
    request: CreateFclFreightRateFreeDayRequest, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = create_fcl_freight_rate_free_day_request(
            request.dict(exclude_none=False)
        )
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/create_fcl_freight_rate_sheet")
def create_rate_sheets(request: CreateRateSheet, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        rate_sheet = create_rate_sheet(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(rate_sheet))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/update_fcl_freight_rate_sheet")
def update_rate_sheets(request: UpdateRateSheet, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]

    try:
        rate_sheet = update_rate_sheet(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(rate_sheet))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/list_fcl_freight_rate_sheets")
def list_rates_sheets(
    filters: str = None,
    stats_required: bool = True,
    page: int = 1,
    page_limit: int = 10,
    sort_by: str = "created_at",
    sort_type: str = "desc",
    pagination_data_required: bool = True,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        response = list_rate_sheets(
            filters,
            stats_required,
            page,
            page_limit,
            sort_by,
            sort_type,
            pagination_data_required,
        )
        return JSONResponse(status_code=200, content=response)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/list_fcl_freight_rate_sheet_stats")
def list_rates_sheet_stat(
    filters: str = None,
    service_provider_id: str = None,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        response = list_rate_sheet_stats(filters, service_provider_id)
        return JSONResponse(status_code=200, content=response)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/get_eligible_fcl_freight_rate_free_day")
def get_eligible_freight_rate_free_day_func(
    filters: str = None,
    sort_by_specificity_type: bool = False,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        resp = get_eligible_fcl_freight_rate_free_day(
            filters, sort_by_specificity_type=sort_by_specificity_type
        )
        return JSONResponse(status_code=200, content=resp)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/get_fcl_freight_weight_slabs_for_rates")
def get_fcl_freight_weight_slabs(
    origin_port_id: str,
    origin_country_id: str,
    destination_port_id: str,
    destination_country_id: str,
    container_size: str,
    container_type: str,
    trade_type: str = None,
    cogo_entity_id: str = None,
    importer_exporter_id: str = None,
    commodity: str = None,
    shipping_line_id: str = None,
    service_provider_id: str = None,
    cargo_weight_per_container: int = 0,
    resp: dict = Depends(authorize_token),
    rates: List[str] | None = Query(None),
):
    request = {
        "origin_port_id": origin_port_id,
        "origin_country_id": origin_country_id,
        "destination_port_id": destination_port_id,
        "destination_country_id": destination_country_id,
        "container_size": container_size,
        "container_type": container_type,
        "commodity": commodity,
        "importer_exporter_id": importer_exporter_id,
        "trade_type": trade_type,
        "shipping_line_id": shipping_line_id,
        "service_provider_id": service_provider_id,
        "cargo_weight_per_container": cargo_weight_per_container,
        "cogo_entity_id": cogo_entity_id,
    }

    if not rates:
        rates = []
    else:
        rates = list(filter(None, rates))

    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        resp = get_fcl_freight_weight_slabs_for_rates(request, rates)
        return JSONResponse(status_code=200, content=resp)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/get_suggested_cogo_assured_fcl_freight_rates")
def get_suggested_cogo_assured_fcl_freight_rates_data(
    container_size: str,
    price: int,
    currency: str,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    try:
        rate_params = {
            "container_size": container_size,
            "price": price,
            "currency": currency,
        }
        data = get_suggested_cogo_assured_fcl_freight_rates(rate_params)
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        # raise
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/list_fcl_freight_rate_deviations")
def list_fcl_freight_rate_deviation(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        data = list_fcl_freight_rate_deviations(filters, page_limit, page)
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/create_fcl_freight_location_cluster")
def create_fcl_freight_location_cluster_func(request: FclLocationCluster):
    try:
        response = create_fcl_freight_location_cluster(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=response)
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/create_cluster_extension_gri_worker")
def create_critical_port_trend_index_data(
    request: CreateCriticalPortTrendIndex, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = create_critical_port_trend_index(request.dict(exclude_none=False))
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/get_fcl_freight_rate_job_stats")
def get_fcl_freight_rate_job_stats_api(
    filters: str = None, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        data = get_fcl_freight_rate_job_stats(filters)
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/list_fcl_freight_rate_jobs")
def list_fcl_freight_rate_jobs_api(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    sort_by: str = "updated_at",
    sort_type: str = "desc",
    generate_csv_url: bool = False,
    pagination_data_required: bool = False,
    includes: str = None,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        data = list_fcl_freight_rate_jobs(
            filters,
            page_limit,
            page,
            sort_by,
            sort_type,
            generate_csv_url,
            pagination_data_required,
            includes,
        )
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/delete_fcl_freight_rate_job")
def delete_fcl_freight_rate_job_api(
    request: DeleteFclFreightRateJob, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
    try:
        rate = delete_fcl_freight_rate_job(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(rate))
    except HTTPException as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/get_fcl_freight_rate_job_csv_url")
def get_fcl_freight_rate_job_csv_url_api(
    filters: str = None, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        data = list_fcl_freight_rate_jobs(filters, generate_csv_url=True)
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/update_charges_yml")
def update_charges_yml_data(serviceChargeType: str):
    try:
        data = update_charges_yml(serviceChargeType)
        return JSONResponse(status_code=200, content={"success": True, "message": data})
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/create_fcl_freight_rate_job")
def create_fcl_freight_rate_job_api(
    request: CreateFclFreightRateJob, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
    source = request.source
    try:
        rate = create_fcl_freight_rate_job(request.dict(exclude_none=True), source)
        return JSONResponse(status_code=200, content=json_encoder(rate))
    except HTTPException as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/get_ltl_freight_rate_job_stats")
def get_ltl_freight_rate_job_stats_api(
    filters: str = None, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        data = get_ltl_freight_rate_job_stats(filters)
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/list_ltl_freight_rate_jobs")
def list_ltl_freight_rate_jobs_api(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    sort_by: str = "updated_at",
    sort_type: str = "desc",
    generate_csv_url: bool = False,
    pagination_data_required: bool = False,
    includes: str = None,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        data = list_ltl_freight_rate_jobs(
            filters,
            page_limit,
            page,
            sort_by,
            sort_type,
            generate_csv_url,
            pagination_data_required,
            includes,
        )
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/delete_ltl_freight_rate_job")
def delete_ltl_freight_rate_job_api(
    request: DeleteLtlFreightRateJob, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
    try:
        rate = delete_ltl_freight_rate_job(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(rate))
    except HTTPException as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/get_ltl_freight_rate_job_csv_url")
def get_ltl_freight_rate_job_csv_url_api(
    filters: str = None, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        data = list_ltl_freight_rate_jobs(filters, generate_csv_url=True)
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/create_ltl_freight_rate_job")
def create_ltl_freight_rate_job_api(
    request: CreateLtlFreightRateJob, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
    source = request.source
    try:
        rate = create_ltl_freight_rate_job(request.dict(exclude_none=True), source)
        return JSONResponse(status_code=200, content=json_encoder(rate))
    except HTTPException as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/get_lcl_freight_rate_job_stats")
def get_lcl_freight_rate_job_stats_api(
    filters: str = None, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        data = get_lcl_freight_rate_job_stats(filters)
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/list_lcl_freight_rate_jobs")
def list_lcl_freight_rate_jobs_api(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    sort_by: str = "updated_at",
    sort_type: str = "desc",
    generate_csv_url: bool = False,
    pagination_data_required: bool = False,
    includes: str = None,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        data = list_lcl_freight_rate_jobs(
            filters,
            page_limit,
            page,
            sort_by,
            sort_type,
            generate_csv_url,
            pagination_data_required,
            includes,
        )
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/delete_lcl_freight_rate_job")
def delete_lcl_freight_rate_job_api(
    request: DeleteLclFreightRateJob, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
    try:
        rate = delete_lcl_freight_rate_job(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(rate))
    except HTTPException as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/get_lcl_freight_rate_job_csv_url")
def get_lcl_freight_rate_job_csv_url_api(
    filters: str = None, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        data = list_lcl_freight_rate_jobs(filters, generate_csv_url=True)
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/create_lcl_freight_rate_job")
def create_lcl_freight_rate_job_api(
    request: CreateLclFreightRateJob, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
    source = request.source
    try:
        rate = create_lcl_freight_rate_job(request.dict(exclude_none=True), source)
        return JSONResponse(status_code=200, content=json_encoder(rate))
    except HTTPException as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/get_lcl_customs_rate_job_stats")
def get_lcl_customs_rate_job_stats_api(
    filters: str = None, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        data = get_lcl_customs_rate_job_stats(filters)
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/list_lcl_customs_rate_jobs")
def list_lcl_customs_rate_jobs_api(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    sort_by: str = "updated_at",
    sort_type: str = "desc",
    generate_csv_url: bool = False,
    pagination_data_required: bool = False,
    includes: str = None,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        data = list_lcl_customs_rate_jobs(
            filters,
            page_limit,
            page,
            sort_by,
            sort_type,
            generate_csv_url,
            pagination_data_required,
            includes,
        )
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/delete_lcl_customs_rate_job")
def delete_lcl_customs_rate_job_api(
    request: DeleteLclCustomsRateJob, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
    try:
        rate = delete_lcl_customs_rate_job(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(rate))
    except HTTPException as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.get("/get_lcl_customs_rate_job_csv_url")
def get_lcl_customs_rate_job_csv_url_api(
    filters: str = None, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        data = list_lcl_customs_rate_jobs(filters, generate_csv_url=True)
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/create_lcl_customs_rate_job")
def create_lcl_customs_rate_job_api(
    request: CreateLclCustomsRateJob, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
    source = request.source
    try:
        rate = create_lcl_customs_rate_job(request.dict(exclude_none=True), source)
        return JSONResponse(status_code=200, content=json_encoder(rate))
    except HTTPException as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/update_fcl_freight_rate_job")
def update_fcl_freight_rate_job_api(
    request: UpdateFclFreightRateJob, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
    try:
        data = update_fcl_freight_rate_job(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/update_ltl_freight_rate_job")
def update_ltl_freight_rate_job_api(
    request: UpdateLtlFreightRateJob, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
    try:
        data = update_ltl_freight_rate_job(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/update_lcl_freight_rate_job")
def update_lcl_freight_rate_job_api(
    request: UpdateLclFreightRateJob, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
    try:
        data = update_lcl_freight_rate_job(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/update_lcl_customs_rate_job")
def update_lcl_customs_rate_job_api(
    request: UpdateLclCustomsRateJob, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
    try:
        data = update_lcl_customs_rate_job(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/update_lcl_customs_rate_job_on_rate_addition")
def update_lcl_customs_rate_job_on_rate_addition_api(
    request: UpdateLclCustomsRateJobOnRateAddition,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
    try:
        data = update_lcl_customs_rate_job_on_rate_addition(
            request.dict(exclude_none=True)
        )
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/update_lcl_freight_rate_job_on_rate_addition")
def update_lcl_freight_rate_job_on_rate_addition_api(
    request: UpdateLclFreightRateJobOnRateAddition,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
    try:
        data = update_lcl_freight_rate_job_on_rate_addition(
            request.dict(exclude_none=True)
        )
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@fcl_freight_router.post("/update_ltl_freight_rate_job_on_rate_addition")
def update_ltl_freight_rate_job_on_rate_addition_api(
    request: UpdateLtlFreightRateJobOnRateAddition,
    resp: dict = Depends(authorize_token),
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
    try:
        data = update_ltl_freight_rate_job_on_rate_addition(
            request.dict(exclude_none=True)
        )
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
    
@fcl_freight_router.get("/get_fcl_freight_rate_local_job_stats")
def get_fcl_freight_rate_local_job_stats_api(
    filters: str = None,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        data = get_fcl_freight_rate_local_job_stats(filters)
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })



@fcl_freight_router.get("/list_fcl_freight_rate_local_jobs")
def list_fcl_freight_rate_local_jobs_api(
    filters: str = None,
    page_limit: int = 10,
    page: int = 1,
    sort_by: str = 'updated_at',
    sort_type: str = 'desc',
    generate_csv_url: bool = False,
    pagination_data_required: bool = False,
    includes: str = None,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        data = list_fcl_freight_rate_local_jobs(filters, page_limit, page, sort_by, sort_type, generate_csv_url, pagination_data_required, includes)
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })

@fcl_freight_router.post("/delete_fcl_freight_rate_local_job")
def delete_fcl_freight_rate_local_job_api(
    request: DeleteFclFreightRateLocalJob, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
    try:
        rate = delete_fcl_freight_rate_local_job(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(rate))
    except HTTPException as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
    
@fcl_freight_router.get('/get_fcl_freight_rate_cards_with_schedules')
def get_fcl_freight_rate_cards_with_schedules_data(
    spot_negotiation_rates: Json = Query(None),
    fcl_freight_rate_cards_params: Json = Query(None),
    sailing_schedules_required: bool = False,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        resp = get_fcl_freight_rate_cards_with_schedules(spot_negotiation_rates, fcl_freight_rate_cards_params, sailing_schedules_required)
        return JSONResponse(status_code=200, content=json_encoder(resp))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
    

@fcl_freight_router.post("/update_schedule_in_fcl_freight_rate")
def update_schedule_in_fcl_freight_rate_data(request: UpdateScheduleInFclFreightRate, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = update_schedule_in_fcl_freight_rate(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })    

@fcl_freight_router.get("/get_fcl_freight_rate_local_job_csv_url")
def get_fcl_freight_rate_local_job_csv_url_api(
    filters: str = None,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        data = list_fcl_freight_rate_local_jobs(filters, generate_csv_url=True)
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
    

@fcl_freight_router.post("/create_fcl_freight_rate_local_job")
def create_fcl_freight_rate_local_job_api(
    request: CreateFclFreightRateLocalJob, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
    source = request.source
    try:
        rate = create_fcl_freight_rate_local_job(request.dict(exclude_none=True), source)
        return JSONResponse(status_code=200, content=json_encoder(rate))
    except HTTPException as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
    
@fcl_freight_router.get('/get_fcl_freight_rate_cards_with_schedules')
def get_fcl_freight_rate_cards_with_schedules_data(
    spot_negotiation_rates: Json = Query(None),
    fcl_freight_rate_cards_params: Json = Query(None),
    sailing_schedules_required: bool = False,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        resp = get_fcl_freight_rate_cards_with_schedules(spot_negotiation_rates, fcl_freight_rate_cards_params, sailing_schedules_required)
        return JSONResponse(status_code=200, content=json_encoder(resp))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
    

@fcl_freight_router.post("/update_schedule_in_fcl_freight_rate")
def update_schedule_in_fcl_freight_rate_data(request: UpdateScheduleInFclFreightRate, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        data = update_schedule_in_fcl_freight_rate(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })    

@fcl_freight_router.post("/update_fcl_freight_rate_local_job")    
def update_fcl_freight_rate_local_job_api(
    request: UpdateFclFreightRateLocalJob, resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
    try:
        data = update_fcl_freight_rate_local_job(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
    
    
@fcl_freight_router.post("/create_fcl_freight_rate_local_feedback")
def create_fcl_freight_rate_local_feedback_data(request: CreateFclFreightRateLocalFeedback, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        rate_id = create_fcl_freight_rate_local_feedback(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(rate_id))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
    
@fcl_freight_router.post("/delete_fcl_freight_rate_local_feedback")
def delete_fcl_freight_rates_local_feedback(request: DeleteFclFreightRateLocalFeedback, resp: dict = Depends(authorize_token)):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)
    if resp["isAuthorized"]:
        request.performed_by_id = resp["setters"]["performed_by_id"]
        request.performed_by_type = resp["setters"]["performed_by_type"]
    try:
        delete_rate = delete_fcl_freight_rate_local_feedback(request.dict(exclude_none=True))
        return JSONResponse(status_code=200, content=json_encoder(delete_rate))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })
    
@fcl_freight_router.get("/list_fcl_freight_rate_local_feedbacks")
def list_fcl_freight_rate_local_feedbacks_data(
    filters: str = None,
    spot_search_details_required: bool = False,
    page_limit: int = 10,
    page: int = 1,
    performed_by_id: str = None,
    is_stats_required: bool = True,
    resp: dict = Depends(authorize_token)
):
    if resp["status_code"] != 200:
        return JSONResponse(status_code=resp["status_code"], content=resp)

    try:
        data = list_fcl_freight_rate_local_feedbacks(filters, spot_search_details_required, page_limit, page, performed_by_id, is_stats_required)
        return JSONResponse(status_code=200, content=json_encoder(data))
    except HTTPException as e:
        raise
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return JSONResponse(status_code=500, content={ "success": False, 'error': str(e) })