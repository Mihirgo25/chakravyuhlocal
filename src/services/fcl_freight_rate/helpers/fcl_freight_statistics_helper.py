from fastapi.encoders import jsonable_encoder
import sentry_sdk


def send_rate_stats(action, freight, request=None):
    try:
        from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
        from services.bramhastra.request_params import ApplyFclFreightRateStatistic
        from services.bramhastra.interactions.apply_fcl_freight_rate_statistic import (
            apply_fcl_freight_rate_statistic,
        )

        keys = [
            FclFreightRate.id.name,
            FclFreightRate.origin_port_id.name,
            FclFreightRate.destination_port_id.name,
            FclFreightRate.origin_main_port_id.name,
            FclFreightRate.destination_main_port_id.name,
            FclFreightRate.origin_country_id.name,
            FclFreightRate.destination_country_id.name,
            FclFreightRate.origin_country_id.name,
            FclFreightRate.destination_country_id.name,
            FclFreightRate.origin_continent_id.name,
            FclFreightRate.destination_continent_id.name,
            FclFreightRate.origin_trade_id.name,
            FclFreightRate.destination_trade_id.name,
            FclFreightRate.shipping_line_id.name,
            FclFreightRate.service_provider_id.name,
            FclFreightRate.validities.name,
            FclFreightRate.mode.name,
            FclFreightRate.commodity.name,
            FclFreightRate.container_size.name,
            FclFreightRate.container_type.name,
            FclFreightRate.containers_count.name,
            FclFreightRate.origin_local_id.name,
            FclFreightRate.destination_local_id.name,
            FclFreightRate.origin_detention_id.name,
            FclFreightRate.destination_detention_id.name,
            FclFreightRate.origin_demurrage_id.name,
            FclFreightRate.destination_demurrage_id.name,
            FclFreightRate.cogo_entity_id.name,
            FclFreightRate.rate_type.name,
            FclFreightRate.tags.name,
            FclFreightRate.sourced_by_id.name,
            FclFreightRate.procured_by_id.name,
            FclFreightRate.created_at.name,
            FclFreightRate.updated_at.name,
        ]

        object = jsonable_encoder({key: getattr(freight, key) for key in keys})

        if request:
            try:
                if request.get("port_to_region_id_mapping"):
                    if object.get("origin_main_port_id"):
                        object["origin_region_id"] = request.get(
                            "port_to_region_id_mapping"
                        )[object.get("origin_main_port_id")]
                    else:
                        object["origin_region_id"] = request.get(
                            "port_to_region_id_mapping"
                        )[object.get("origin_port_id")]

                    if object.get("destination_main_port_id"):
                        object["destination_region_id"] = request.get(
                            "port_to_region_id_mapping"
                        )[object.get("destination_main_port_id")]
                    else:
                        object["destination_region_id"] = request.get(
                            "port_to_region_id_mapping"
                        )[object.get("destination_port_id")]
            except Exception:
                pass

            for k, v in request.items():
                if k in {
                    "source_id",
                    "source",
                    "performed_by_id",
                    "performed_by_type",
                    "tag",
                }:
                    object[k] = v

        apply_fcl_freight_rate_statistic(
            ApplyFclFreightRateStatistic(action=action, params={"freight": object})
        )
    except Exception as e:
        sentry_sdk.capture_exception(e)


def send_request_stats(action, obj):
    try:
        from services.bramhastra.interactions.apply_fcl_freight_rate_request_statistic import (
            apply_fcl_freight_rate_request_statistic,
        )
        from services.fcl_freight_rate.models.fcl_freight_rate_request import (
            FclFreightRateRequest,
        )
        from services.bramhastra.request_params import (
            ApplyFclFreightRateRequestStatistic,
        )

        keys = [
            FclFreightRateRequest.id.name,
            FclFreightRateRequest.origin_port_id.name,
            FclFreightRateRequest.destination_port_id.name,
            FclFreightRateRequest.origin_country_id.name,
            FclFreightRateRequest.destination_country_id.name,
            FclFreightRateRequest.origin_continent_id.name,
            FclFreightRateRequest.destination_continent_id.name,
            FclFreightRateRequest.origin_trade_id.name,
            FclFreightRateRequest.destination_trade_id.name,
            FclFreightRateRequest.source.name,
            FclFreightRateRequest.source_id.name,
            FclFreightRateRequest.closing_remarks.name,
            FclFreightRateRequest.commodity.name,
            FclFreightRateRequest.containers_count.name,
            FclFreightRateRequest.created_at.name,
            FclFreightRateRequest.updated_at.name,
            FclFreightRateRequest.performed_by_org_id.name,
            FclFreightRateRequest.performed_by_id.name,
            FclFreightRateRequest.serial_id.name,
            FclFreightRateRequest.request_type.name,
            FclFreightRateRequest.status.name,
            FclFreightRateRequest.container_size.name,
            FclFreightRateRequest.closed_by_id.name,
            FclFreightRateRequest.closing_remarks.name,
        ]

        if action == "create":
            obj = jsonable_encoder({key: getattr(obj, key) for key in keys})

        if action == "update":
            if (not isinstance(obj, dict)) or ("ignore" in obj and obj["ignore"]):
                return
            obj["id"] = obj.pop("fcl_freight_rate_request_id")

        apply_fcl_freight_rate_request_statistic(
            ApplyFclFreightRateRequestStatistic(
                action=action, params=jsonable_encoder(obj)
            )
        )
    except Exception as e:
        sentry_sdk.capture_exception(e)


def send_feedback_statistics(action, feedback, request=None):
    try:
        from configs.fcl_freight_rate_constants import (
            REQUIRED_FEEDBACK_STATS_REQUEST_KEYS,
        )
        from services.bramhastra.interactions.apply_feedback_fcl_freight_rate_statistic import (
            apply_feedback_fcl_freight_rate_statistic,
        )
        from services.bramhastra.request_params import (
            ApplyFeedbackFclFreightRateStatistics,
        )
        from services.fcl_freight_rate.models.fcl_freight_rate_feedback import (
            FclFreightRateFeedback,
        )

        keys = [
            FclFreightRateFeedback.id.name,
            FclFreightRateFeedback.source.name,
            FclFreightRateFeedback.source_id.name,
            FclFreightRateFeedback.closed_by_id.name,
            FclFreightRateFeedback.fcl_freight_rate_id.name,
            FclFreightRateFeedback.validity_id.name,
            FclFreightRateFeedback.service_provider_id.name,
            FclFreightRateFeedback.serial_id.name,
            FclFreightRateFeedback.created_at.name,
            FclFreightRateFeedback.updated_at.name,
            FclFreightRateFeedback.performed_by_id.name,
            FclFreightRateFeedback.performed_by_org_id.name,
            FclFreightRateFeedback.feedback_type.name,
            FclFreightRateFeedback.cogo_entity_id.name,
            FclFreightRateFeedback.closing_remarks.name,
            FclFreightRateFeedback.status.name,
            FclFreightRateFeedback.feedbacks.name,
            FclFreightRateFeedback.preferred_freight_rate.name,
            FclFreightRateFeedback.preferred_freight_rate_currency.name,
        ]

        object = jsonable_encoder({key: getattr(feedback, key) for key in keys})

        if request:
            for k, v in request.items():
                if k in REQUIRED_FEEDBACK_STATS_REQUEST_KEYS:
                    object[k] = v

        apply_feedback_fcl_freight_rate_statistic(
            ApplyFeedbackFclFreightRateStatistics(action=action, params=object)
        )
    except Exception as e:
        sentry_sdk.capture_exception(e)


def send_feedback_delete_stats(obj):
    try:
        from services.fcl_freight_rate.models.fcl_freight_rate_feedback import (
            FclFreightRateFeedback,
        )
        from services.bramhastra.request_params import (
            ApplyFeedbackFclFreightRateStatistics,
        )
        from services.bramhastra.interactions.apply_feedback_fcl_freight_rate_statistic import (
            apply_feedback_fcl_freight_rate_statistic,
        )

        action = "delete"

        keys = [
            FclFreightRateFeedback.id.name,
            FclFreightRateFeedback.status.name,
            FclFreightRateFeedback.closed_by_id.name,
            FclFreightRateFeedback.closing_remarks.name,
            FclFreightRateFeedback.fcl_freight_rate_id.name,
            FclFreightRateFeedback.validity_id.name,
            FclFreightRateFeedback.source.name,
            FclFreightRateFeedback.source_id.name,
        ]
        params = jsonable_encoder({key: getattr(obj, key) for key in keys})

        apply_feedback_fcl_freight_rate_statistic(
            ApplyFeedbackFclFreightRateStatistics(action=action, params=params)
        )
    except Exception as e:
        sentry_sdk.capture_exception(e)


def send_request_delete_stats(obj):
    try:
        from services.bramhastra.interactions.apply_fcl_freight_rate_request_statistic import (
            apply_fcl_freight_rate_request_statistic,
        )
        from services.fcl_freight_rate.models.fcl_freight_rate_request import (
            FclFreightRateRequest,
        )
        from services.bramhastra.request_params import (
            ApplyFclFreightRateRequestStatistic,
        )

        keys = [
            FclFreightRateRequest.id.name,
            FclFreightRateRequest.origin_port_id.name,
            FclFreightRateRequest.destination_port_id.name,
            FclFreightRateRequest.origin_country_id.name,
            FclFreightRateRequest.destination_country_id.name,
            FclFreightRateRequest.origin_continent_id.name,
            FclFreightRateRequest.destination_continent_id.name,
            FclFreightRateRequest.origin_trade_id.name,
            FclFreightRateRequest.destination_trade_id.name,
            FclFreightRateRequest.source.name,
            FclFreightRateRequest.source_id.name,
            FclFreightRateRequest.closing_remarks.name,
            FclFreightRateRequest.commodity.name,
            FclFreightRateRequest.containers_count.name,
            FclFreightRateRequest.created_at.name,
            FclFreightRateRequest.updated_at.name,
            FclFreightRateRequest.performed_by_org_id.name,
            FclFreightRateRequest.performed_by_id.name,
            FclFreightRateRequest.serial_id.name,
            FclFreightRateRequest.request_type.name,
            FclFreightRateRequest.status.name,
            FclFreightRateRequest.container_size.name,
            FclFreightRateRequest.closed_by_id.name,
            FclFreightRateRequest.closing_remarks.name,
        ]

        action = "delete"

        params = jsonable_encoder({key: getattr(obj, key) for key in keys})

        apply_fcl_freight_rate_request_statistic(
            ApplyFclFreightRateRequestStatistic(action=action, params=params)
        )
    except Exception as e:
        sentry_sdk.capture_exception(e)
