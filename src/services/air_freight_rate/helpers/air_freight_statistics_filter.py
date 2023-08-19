from fastapi.encoders import jsonable_encoder
from playhouse.shortcuts import model_to_dict

def send_freight_rate_stats(action,freight):
    from services.bramhastra.interactions.apply_air_freight_rate_statistic import (
        apply_air_freight_rate_statistic,
    )
    from services.bramhastra.request_params import ApplyAirFreightRateStatistic
    from services.air_freight_rate.models.air_freight_rate import AirFreightRate

    freight = model_to_dict(
        freight,
        only=[
            AirFreightRate.id,
            AirFreightRate.origin_airport_id,
            AirFreightRate.destination_airport_id,
            AirFreightRate.origin_country_id,
            AirFreightRate.destination_country_id,
            AirFreightRate.origin_continent_id,
            AirFreightRate.destination_continent_id,
            AirFreightRate.origin_trade_id,
            AirFreightRate.destination_trade_id,
            AirFreightRate.airline_id,
            AirFreightRate.service_provider_id,
            AirFreightRate.accuracy,
            AirFreightRate.validities,
            AirFreightRate.source,
            AirFreightRate.commodity,
            AirFreightRate.commodity_type,
            AirFreightRate.commodity_sub_type,
            AirFreightRate.operation_type,
            AirFreightRate.origin_local_id,
            AirFreightRate.destination_local_id,
            AirFreightRate.surcharge_id,
            AirFreightRate.price_type,
            AirFreightRate.rate_type,
            AirFreightRate.shipment_type,
            AirFreightRate.stacking_type,
            AirFreightRate.cogo_entity_id,
            AirFreightRate.sourced_by_id,
            AirFreightRate.procured_by_id,
            AirFreightRate.created_at,
            AirFreightRate.updated_at
        ],
    )
    
    apply_air_freight_rate_statistic(ApplyAirFreightRateStatistic(action = action,create_params=jsonable_encoder({'freight': freight})))
    
    
    
def set_feedback_statistics(action, request, feedback):
    from services.bramhastra.interactions.apply_feedback_air_freight_rate_statistic import (
        apply_feedback_air_freight_rate_statistic,
    )
    from services.bramhastra.request_params import ApplyFeedbackAirFreightRateStatistics
    from playhouse.shortcuts import model_to_dict
    from configs.fcl_freight_rate_constants import REQUIRED_FEEDBACK_STATS_REQUEST_KEYS
    from libs.json_encoder import json_encoder
    from services.air_freight_rate.models.air_freight_rate_feedback import AirFreightRateFeedback

    params = model_to_dict(
        feedback,
        only=[
            AirFreightRateFeedback.id,
            AirFreightRateFeedback.source,
            AirFreightRateFeedback.source_id,
            AirFreightRateFeedback.closed_by_id,
            AirFreightRateFeedback.air_freight_rate_id,
            AirFreightRateFeedback.validity_id,
            AirFreightRateFeedback.service_provider_id,
            AirFreightRateFeedback.serial_id,
            AirFreightRateFeedback.created_at,
            AirFreightRateFeedback.updated_at,
            AirFreightRateFeedback.performed_by_id,
            AirFreightRateFeedback.performed_by_org_id,
            AirFreightRateFeedback.feedback_type,
        ],
    )

    for k, v in request.items():
        if k in REQUIRED_FEEDBACK_STATS_REQUEST_KEYS:
            params[k] = v 
        
    apply_feedback_air_freight_rate_statistic(
        ApplyFeedbackAirFreightRateStatistics(
            action=action, params=json_encoder(params)
        )
    )