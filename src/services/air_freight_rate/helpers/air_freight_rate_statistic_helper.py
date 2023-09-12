from playhouse.shortcuts import model_to_dict
from fastapi.encoders import jsonable_encoder
import sentry_sdk


def send_rate_stats(action, request, freight):
    try:
        from services.air_freight_rate.models.air_freight_rate import AirFreightRate
        from services.bramhastra.request_params import ApplyAirFreightRateStatistic
        from services.bramhastra.interactions.apply_air_freight_rate_statistic import (
            apply_air_freight_rate_statistic,
        )

        object = jsonable_encoder(
            model_to_dict(
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
                    AirFreightRate.source,
                    AirFreightRate.created_at,
                    AirFreightRate.updated_at,
                    AirFreightRate.commodity,
                    AirFreightRate.commodity_type,
                    AirFreightRate.commodity_sub_type,
                    AirFreightRate.operation_type,
                    AirFreightRate.shipment_type,
                    AirFreightRate.stacking_type,
                    AirFreightRate.origin_local_id,
                    AirFreightRate.destination_local_id,
                    AirFreightRate.surcharge_id,
                    AirFreightRate.cogo_entity_id,
                    AirFreightRate.price_type,
                    AirFreightRate.rate_type,
                    AirFreightRate.sourced_by_id,
                    AirFreightRate.procured_by_id,
                    AirFreightRate.validities,
                    AirFreightRate.height,
                    AirFreightRate.breadth,
                    AirFreightRate.length,
                    AirFreightRate.maximum_weight,
                    AirFreightRate.currency,
                    AirFreightRate.discount_type,
                    AirFreightRate.importer_exporter_id,
                    AirFreightRate.rate_not_available_entry,              
                ],
            )
        )

        for k, v in request.items():
            if k in {"source_id", "source", "performed_by_id", "performed_by_type"}:
                object[k] = v
        
        apply_air_freight_rate_statistic(
            ApplyAirFreightRateStatistic(action=action, params={"freight": object})
        )
    except Exception as e:
        sentry_sdk.capture_exception(e)
