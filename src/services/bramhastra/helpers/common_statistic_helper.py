from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)


def get_fcl_freight_identifier(rate_id, validity_id) -> str:
    return "".join([str(rate_id), str(validity_id)]).replace("-", "")


def get_air_freight_identifier(rate_id, validity_id, lower_limit, upper_limit) -> str:
    return "".join(
        [str(rate_id), str(validity_id), str(lower_limit), str(upper_limit)]
    ).replace("-", "")


REQUIRED_ACTION_FIELDS = [
    FclFreightRateStatistic.rate_id,
    FclFreightRateStatistic.validity_id,
    FclFreightRateStatistic.validity_start,
    FclFreightRateStatistic.validity_end,
    FclFreightRateStatistic.mode,
    FclFreightRateStatistic.source,
    FclFreightRateStatistic.source_id,
    FclFreightRateStatistic.bas_currency,
    FclFreightRateStatistic.bas_price,
    FclFreightRateStatistic.bas_standard_price,
    FclFreightRateStatistic.price,
    FclFreightRateStatistic.standard_price,
    FclFreightRateStatistic.rate_type,
    FclFreightRateStatistic.market_price,
    FclFreightRateStatistic.shipping_line_id,
    FclFreightRateStatistic.service_provider_id,
    FclFreightRateStatistic.commodity,
    FclFreightRateStatistic.container_size,
    FclFreightRateStatistic.container_type,
    FclFreightRateStatistic.origin_trade_id,
    FclFreightRateStatistic.destination_trade_id,
    FclFreightRateStatistic.origin_continent_id,
    FclFreightRateStatistic.destination_continent_id,
    FclFreightRateStatistic.origin_country_id,
    FclFreightRateStatistic.destination_country_id,
    FclFreightRateStatistic.origin_port_id,
    FclFreightRateStatistic.destination_port_id,
    FclFreightRateStatistic.origin_main_port_id,
    FclFreightRateStatistic.destination_main_port_id,
    FclFreightRateStatistic.origin_region_id,
    FclFreightRateStatistic.destination_region_id,
    FclFreightRateStatistic.performed_by_id,
    FclFreightRateStatistic.procured_by_id,
    FclFreightRateStatistic.sourced_by_id,
]
