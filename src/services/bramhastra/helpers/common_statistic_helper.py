from peewee import Model


RATE_REQUIRED_FIELDS = {
    "id",
    "origin_port_id",
    "destination_port_id",
    "origin_main_port_id",
    "destination_main_port_id",
    "origin_country_id",
    "destination_country_id",
    "origin_country_id",
    "destination_country_id",
    "origin_continent_id",
    "destination_continent_id",
    "origin_trade_id",
    "destination_trade_id",
    "shipping_line_id",
    "service_provider_id",
    "validities",
    "mode",
    "commodity",
    "container_size",
    "container_type",
    "containers_count",
    "origin_local_id",
    "destination_local_id",
    "origin_detention_id",
    "destination_detention_id",
    "origin_demurrage_id",
    "destination_demurrage_id",
    "cogo_entity_id",
    "rate_type",
    "tags",
    "sourced_by_id",
    "procured_by_id",
    "created_at",
    "updated_at",
}


def get_fcl_freight_identifier(rate_id, validity_id) -> str:
    return "".join([str(rate_id), str(validity_id)]).replace("-", "")


def get_air_freight_identifier(rate_id, validity_id, lower_limit, upper_limit) -> str:
    return "".join(
        [str(rate_id), str(validity_id), str(lower_limit), str(upper_limit)]
    ).replace("-", "")


def create_fcl_freight_rate_statistic_fallback(rate_id, validity_id) -> Model:
    from services.fcl_freight_rate.interaction.list_fcl_freight_rates import (
        list_fcl_freight_rates,
    )
    from enums.global_enums import Action
    from services.bramhastra.request_params import ApplyFclFreightRateStatistic
    from services.bramhastra.interactions.apply_fcl_freight_rate_statistic import (
        apply_fcl_freight_rate_statistic,
    )
    from services.bramhastra.models.fcl_freight_rate_statistic import (
        FclFreightRateStatistic,
    )

    fcl_freight_rates = list_fcl_freight_rates(
        filters={"id": rate_id, "rate_type": "all"},
        includes={k: 1 for k in RATE_REQUIRED_FIELDS},
        pagination_data_required=False,
    ).get("list", [])
    if fcl_freight_rates:
        fcl_freight_rate = fcl_freight_rates[0]
        if len(fcl_freight_rate["validities"]) > 1:
            fcl_freight_rate["validities"] = [
                validity
                for validity in fcl_freight_rate["validities"]
                if validity["id"] == validity_id
            ]
        apply_fcl_freight_rate_statistic(
            ApplyFclFreightRateStatistic(
                action=Action.create, params={"freight": fcl_freight_rate}
            )
        )
        if (
            fcl_freight_rate_statistic := FclFreightRateStatistic.select()
            .where(
                FclFreightRateStatistic.identifier
                == get_fcl_freight_identifier(rate_id, validity_id)
            )
            .first()
        ):
            return fcl_freight_rate_statistic
