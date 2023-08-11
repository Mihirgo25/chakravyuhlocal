from playhouse.shortcuts import model_to_dict
from fastapi.encoders import jsonable_encoder


def send_rate_stats(action, request, freight):
    from celery_worker import apply_fcl_freight_rate_statistic_delay
    from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate

    object = jsonable_encoder(
        model_to_dict(
            freight,
            only=[
                FclFreightRate.id,
                FclFreightRate.origin_port_id,
                FclFreightRate.destination_port_id,
                FclFreightRate.origin_main_port_id,
                FclFreightRate.destination_main_port_id,
                FclFreightRate.origin_country_id,
                FclFreightRate.destination_country_id,
                FclFreightRate.origin_country_id,
                FclFreightRate.destination_country_id,
                FclFreightRate.origin_trade_id,
                FclFreightRate.destination_trade_id,
                FclFreightRate.shipping_line_id,
                FclFreightRate.service_provider_id,
                FclFreightRate.accuracy,
                FclFreightRate.validities,
                FclFreightRate.mode,
                FclFreightRate.commodity,
                FclFreightRate.container_size,
                FclFreightRate.container_type,
                FclFreightRate.containers_count,
                FclFreightRate.origin_local_id,
                FclFreightRate.destination_local_id,
                FclFreightRate.origin_detention_id,
                FclFreightRate.destination_detention_id,
                FclFreightRate.origin_demurrage_id,
                FclFreightRate.destination_demurrage_id,
                FclFreightRate.cogo_entity_id,
                FclFreightRate.rate_type,
                FclFreightRate.tags,
                FclFreightRate.sourced_by_id,
                FclFreightRate.procured_by_id,
                FclFreightRate.created_at,
                FclFreightRate.updated_at,
            ],
        )
    )

    for k, v in request.items():
        if k in {"source_id", "source"}:
            object[k] = v

    apply_fcl_freight_rate_statistic_delay.apply_async(
        kwargs={"action": action, "params": {"freight": object}}, queue="statistics"
    )


def send_request_stats(obj):
    from services.bramhastra.request_params import ApplyFclFreightRateRequestStatistic
    from services.bramhastra.interactions.apply_fcl_freight_rate_request_statistic import (
        apply_fcl_freight_rate_request_statistic,
    )
    from services.fcl_freight_rate.models.fcl_freight_rate_request import (
        FclFreightRateRequest,
    )

    action = "create"
    params = jsonable_encoder(
        model_to_dict(
            obj,
            only=[
                FclFreightRateRequest.id,
                FclFreightRateRequest.status,
                FclFreightRateRequest.closed_by_id,
                FclFreightRateRequest.closing_remarks,
            ],
        )
    )

    apply_fcl_freight_rate_request_statistic(
        ApplyFclFreightRateRequestStatistic(action=action, params=params)
    )


def send_feedback_statistics(action, feedback, request=None):
    from configs.fcl_freight_rate_constants import REQUIRED_FEEDBACK_STATS_REQUEST_KEYS
    from celery_worker import apply_feedback_fcl_freight_rate_statistic_delay
    from services.fcl_freight_rate.models.fcl_freight_rate_feedback import (
        FclFreightRateFeedback,
    )

    feedback = feedback.refresh()

    object = model_to_dict(
        feedback,
        only=[
            FclFreightRateFeedback.id,
            FclFreightRateFeedback.source,
            FclFreightRateFeedback.source_id,
            FclFreightRateFeedback.closed_by_id,
            FclFreightRateFeedback.fcl_freight_rate_id,
            FclFreightRateFeedback.validity_id,
            FclFreightRateFeedback.service_provider_id,
            FclFreightRateFeedback.serial_id,
            FclFreightRateFeedback.created_at,
            FclFreightRateFeedback.updated_at,
            FclFreightRateFeedback.performed_by_id,
            FclFreightRateFeedback.performed_by_org_id,
            FclFreightRateFeedback.feedback_type,
            FclFreightRateFeedback.cogo_entity_id,
            FclFreightRateFeedback.closing_remarks,
            FclFreightRateFeedback.status,
            FclFreightRateFeedback.feedbacks,
        ],
    )

    if request:
        for k, v in request.items():
            if k in REQUIRED_FEEDBACK_STATS_REQUEST_KEYS:
                object[k] = v

    apply_feedback_fcl_freight_rate_statistic_delay.apply_async(
        kwargs={"action": action, "params": object}, queue="statistics"
    )


def send_feedback_delete_stats(obj):
    from services.fcl_freight_rate.models.fcl_freight_rate_feedback import (
        FclFreightRateFeedback,
    )
    from celery_worker import apply_feedback_fcl_freight_rate_statistic_delay

    action = "delete"
    params = jsonable_encoder(
        model_to_dict(
            obj,
            only=[
                FclFreightRateFeedback.id,
                FclFreightRateFeedback.status,
                FclFreightRateFeedback.closed_by_id,
                FclFreightRateFeedback.closing_remarks,
            ],
        )
    )
    apply_feedback_fcl_freight_rate_statistic_delay.apply_async(
        kwargs={"action": action, "params": params}, queue="statistics"
    )


def send_delete_request_stats(obj):
    from services.bramhastra.interactions.apply_fcl_freight_rate_request_statistic import (
        apply_fcl_freight_rate_request_statistic,
    )
    from services.fcl_freight_rate.models.fcl_freight_rate_request import (
        FclFreightRateRequest,
    )
    from services.bramhastra.request_params import ApplyFclFreightRateRequestStatistic

    action = "delete"
    params = jsonable_encoder(
        model_to_dict(
            obj,
            only=[
                FclFreightRateRequest.id,
                FclFreightRateRequest.status,
                FclFreightRateRequest.closed_by_id,
                FclFreightRateRequest.closing_remarks,
            ],
        )
    )
    apply_fcl_freight_rate_request_statistic(
        ApplyFclFreightRateRequestStatistic(action=action, params=params)
    )


def send_update_request_stats(obj):
    from services.bramhastra.interactions.apply_fcl_freight_rate_request_statistic import (
        apply_fcl_freight_rate_request_statistic,
    )
    from services.fcl_freight_rate.models.fcl_freight_rate_request import (
        FclFreightRateRequest,
    )
    from services.bramhastra.request_params import ApplyFclFreightRateRequestStatistic
    action = 'update'
    params = jsonable_encoder(model_to_dict(obj,only = [FclFreightRateRequest.id,FclFreightRateRequest.status,FclFreightRateRequest.closed_by_id,FclFreightRateRequest.closing_remarks]))
    
    apply_fcl_freight_rate_request_statistic(ApplyFclFreightRateRequestStatistic(action = action,params = params))