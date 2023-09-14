from services.bramhastra.models.spot_search_fcl_freight_rate_statistic import (
    SpotSearchFclFreightRateStatistic,
)
from services.bramhastra.helpers.common_statistic_helper import get_identifier
from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)

RATE_FIELDS = [
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
    FclFreightRateStatistic.destination_region_id
]


class SpotSearch:
    def __init__(self, params) -> None:
        self.common_param = params.dict(exclude={"rates"})
        self.spot_search_id = params.spot_search_id
        self.spot_search_params = []
        self.rates = params.rates
        self.increment_keys = {"spot_search_count"}
        self.clickhouse_client = None

    def set_format_and_existing_rate_stats(self):
        for rate in self.rates:
            param = self.common_param.copy()
            rate_dict = rate.dict(exclude={"payment_term", "schedule_type"})
            param.update(rate_dict)

            fcl_freight_rate_statistic = (
                FclFreightRateStatistic.select()
                .where(
                    FclFreightRateStatistic.identifier == get_identifier(**rate_dict)
                )
                .first()
            )
            
            if not fcl_freight_rate_statistic:
                continue
                   
            for k in self.increment_keys:
                setattr(
                    fcl_freight_rate_statistic,
                    k,
                    getattr(fcl_freight_rate_statistic, k) + 1,
                )
            fcl_freight_rate_statistic.updated_at = param["updated_at"]

            fcl_freight_rate_statistic.save()

            if fcl_freight_rate_statistic:
                param["fcl_freight_rate_statistic_id"] = fcl_freight_rate_statistic.id
                self.spot_search_params.append(param)

    def set_new_stats(self) -> int:
        return SpotSearchFclFreightRateStatistic.insert_many(
            self.spot_search_params
        ).execute()
