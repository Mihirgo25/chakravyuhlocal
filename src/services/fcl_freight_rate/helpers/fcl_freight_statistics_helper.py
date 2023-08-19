from playhouse.shortcuts import model_to_dict
from fastapi.encoders import jsonable_encoder


def send_rate_stats(action, request, freight):
    from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
    from services.bramhastra.request_params import ApplyFclFreightRateStatistic
    from services.bramhastra.interactions.apply_fcl_freight_rate_statistic import apply_fcl_freight_rate_statistic

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
                FclFreightRate.origin_continent_id,
                FclFreightRate.destination_continent_id,
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
    
    try:
        if object.get('origin_main_port_id'):
            object['origin_region_id'] = request.get('port_to_region_id_mapping')[object.get('origin_main_port_id')]
        else:
            object['origin_region_id']  = request.get('port_to_region_id_mapping')[object.get('origin_port_id')]
            
        if object.get('destination_main_port_id'):
            object['destination_region_id'] = request.get('port_to_region_id_mapping')[object.get('destination_main_port_id')]
        else:
            object['destination_region_id']  = request.get('port_to_region_id_mapping')[object.get('destination_port_id')]
    except Exception:
        pass

    for k, v in request.items():
        if k in {"source_id", "source"}:
            object[k] = v
            
    apply_fcl_freight_rate_statistic(ApplyFclFreightRateStatistic(action = action,params = {'freight': object}))


def send_request_stats(action, obj):
    from services.bramhastra.interactions.apply_fcl_freight_rate_request_statistic import apply_fcl_freight_rate_request_statistic
    from services.fcl_freight_rate.models.fcl_freight_rate_request import (
        FclFreightRateRequest,
    )
    from services.bramhastra.request_params import ApplyFclFreightRateRequestStatistic

    if action == "create":
        obj = obj.refresh()

        obj = model_to_dict(
            obj,
            only=[
                FclFreightRateRequest.id,
                FclFreightRateRequest.origin_port_id,
                FclFreightRateRequest.destination_port_id,
                FclFreightRateRequest.origin_country_id,
                FclFreightRateRequest.destination_country_id,
                FclFreightRateRequest.origin_continent_id,
                FclFreightRateRequest.destination_continent_id,
                FclFreightRateRequest.origin_trade_id,
                FclFreightRateRequest.destination_trade_id,
                FclFreightRateRequest.source,
                FclFreightRateRequest.source_id,
                FclFreightRateRequest.closing_remarks,
                FclFreightRateRequest.commodity,
                FclFreightRateRequest.containers_count,
                FclFreightRateRequest.created_at,
                FclFreightRateRequest.updated_at,
                FclFreightRateRequest.performed_by_org_id,
                FclFreightRateRequest.performed_by_id,
                FclFreightRateRequest.serial_id,
                FclFreightRateRequest.request_type,
                FclFreightRateRequest.status,
                FclFreightRateRequest.container_size,
                FclFreightRateRequest.closed_by_id,
                FclFreightRateRequest.closing_remarks,
            ],
        )

    if action == "update":
        if (not isinstance(obj,dict)) or ("ignore" in obj and obj["ignore"]):
            return
        obj["id"] = obj.pop("fcl_freight_rate_request_id")
    
    apply_fcl_freight_rate_request_statistic(ApplyFclFreightRateRequestStatistic(action = action,params = jsonable_encoder(obj)))


def send_feedback_statistics(action, feedback, request=None):
    from configs.fcl_freight_rate_constants import REQUIRED_FEEDBACK_STATS_REQUEST_KEYS
    from services.bramhastra.interactions.apply_feedback_fcl_freight_rate_statistic import apply_feedback_fcl_freight_rate_statistic
    from services.bramhastra.request_params import ApplyFeedbackFclFreightRateStatistics
    from services.fcl_freight_rate.models.fcl_freight_rate_feedback import (
        FclFreightRateFeedback,
    )

    feedback = feedback.refresh()

    object = jsonable_encoder(
        model_to_dict(
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
                FclFreightRateFeedback.preferred_freight_rate,
                FclFreightRateFeedback.preferred_freight_rate_currency,
            ],
        )
    )

    if request:
        for k, v in request.items():
            if k in REQUIRED_FEEDBACK_STATS_REQUEST_KEYS:
                object[k] = v

    apply_feedback_fcl_freight_rate_statistic(ApplyFeedbackFclFreightRateStatistics(action = action,params = object))


def send_feedback_delete_stats(obj):
    from services.fcl_freight_rate.models.fcl_freight_rate_feedback import (
        FclFreightRateFeedback,
    )
    from services.bramhastra.request_params import ApplyFeedbackFclFreightRateStatistics
    from services.bramhastra.interactions.apply_feedback_fcl_freight_rate_statistic import apply_feedback_fcl_freight_rate_statistic

    obj = obj.refresh()

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
    
    apply_feedback_fcl_freight_rate_statistic(ApplyFeedbackFclFreightRateStatistics(action = action,params = params))


def send_request_delete_stats(obj):
    from services.bramhastra.interactions.apply_fcl_freight_rate_request_statistic import apply_fcl_freight_rate_request_statistic
    from services.fcl_freight_rate.models.fcl_freight_rate_request import (
        FclFreightRateRequest,
    )
    from services.bramhastra.request_params import ApplyFclFreightRateRequestStatistic

    obj = obj.refresh()

    action = "delete"

    params = jsonable_encoder(
        model_to_dict(
            obj,
            only=[
                FclFreightRateRequest.id,
                FclFreightRateRequest.origin_port_id,
                FclFreightRateRequest.destination_port_id,
                FclFreightRateRequest.origin_country_id,
                FclFreightRateRequest.destination_country_id,
                FclFreightRateRequest.origin_continent_id,
                FclFreightRateRequest.destination_continent_id,
                FclFreightRateRequest.origin_trade_id,
                FclFreightRateRequest.destination_trade_id,
                FclFreightRateRequest.source,
                FclFreightRateRequest.source_id,
                FclFreightRateRequest.closing_remarks,
                FclFreightRateRequest.commodity,
                FclFreightRateRequest.containers_count,
                FclFreightRateRequest.created_at,
                FclFreightRateRequest.updated_at,
                FclFreightRateRequest.performed_by_org_id,
                FclFreightRateRequest.performed_by_id,
                FclFreightRateRequest.serial_id,
                FclFreightRateRequest.request_type,
                FclFreightRateRequest.status,
                FclFreightRateRequest.container_size,
                FclFreightRateRequest.closed_by_id,
                FclFreightRateRequest.closing_remarks,
            ],
        )
    )
    
    apply_fcl_freight_rate_request_statistic(ApplyFclFreightRateRequestStatistic(action = action,params = params))
