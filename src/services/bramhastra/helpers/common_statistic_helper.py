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
    FclFreightRateStatistic.currency.name,
    FclFreightRateStatistic.rate_id.name,
    FclFreightRateStatistic.validity_id.name,
    FclFreightRateStatistic.validity_start.name,
    FclFreightRateStatistic.validity_end.name,
    FclFreightRateStatistic.mode.name,
    FclFreightRateStatistic.source.name,
    FclFreightRateStatistic.source_id.name,
    FclFreightRateStatistic.bas_currency.name,
    FclFreightRateStatistic.bas_price.name,
    FclFreightRateStatistic.bas_standard_price.name,
    FclFreightRateStatistic.price.name,
    FclFreightRateStatistic.standard_price.name,
    FclFreightRateStatistic.rate_type.name,
    FclFreightRateStatistic.market_price.name,
    FclFreightRateStatistic.shipping_line_id.name,
    FclFreightRateStatistic.service_provider_id.name,
    FclFreightRateStatistic.commodity.name,
    FclFreightRateStatistic.container_size.name,
    FclFreightRateStatistic.container_type.name,
    FclFreightRateStatistic.origin_trade_id.name,
    FclFreightRateStatistic.destination_trade_id.name,
    FclFreightRateStatistic.origin_continent_id.name,
    FclFreightRateStatistic.destination_continent_id.name,
    FclFreightRateStatistic.origin_country_id.name,
    FclFreightRateStatistic.destination_country_id.name,
    FclFreightRateStatistic.origin_port_id.name,
    FclFreightRateStatistic.destination_port_id.name,
    FclFreightRateStatistic.origin_main_port_id.name,
    FclFreightRateStatistic.destination_main_port_id.name,
    FclFreightRateStatistic.origin_region_id.name,
    FclFreightRateStatistic.destination_region_id.name,
    FclFreightRateStatistic.performed_by_id.name,
    FclFreightRateStatistic.procured_by_id.name,
    FclFreightRateStatistic.sourced_by_id.name,
    FclFreightRateStatistic.parent_mode.name,
    FclFreightRateStatistic.source.name,
    FclFreightRateStatistic.rate_created_at.name,
    FclFreightRateStatistic.rate_updated_at.name,
    FclFreightRateStatistic.validity_created_at.name,
    FclFreightRateStatistic.validity_updated_at.name,
    FclFreightRateStatistic.bas_currency.name
]
