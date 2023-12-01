from services.bramhastra.helpers.common_statistic_helper import (
    get_air_freight_identifier,
    create_air_freight_rate_statistic_fallback,
)
from services.bramhastra.models.air_freight_rate_statistic import (
    AirFreightRateStatistic,
)
from services.bramhastra.models.air_freight_action import AirFreightAction
from typing import Union
from peewee import Model

COMMON_PARAMS = {
    # AirFreightAction.spot_search_air_freight_service_id.name,
    # AirFreightAction.spot_search_id.name,
    AirFreightAction.origin_airport_id.name,
    AirFreightAction.destination_airport_id.name,
    AirFreightAction.origin_country_id.name,
    AirFreightAction.destination_country_id.name,
    AirFreightAction.origin_continent_id.name,
    AirFreightAction.destination_continent_id.name,
    AirFreightAction.origin_trade_id.name,
    AirFreightAction.destination_trade_id.name,
    AirFreightAction.container_size.name,
    AirFreightAction.container_type.name,
    # AirFreightAction.containers_count.name,
    AirFreightAction.commodity_type.name,
    AirFreightAction.commodity_sub_type.name,
    AirFreightAction.created_at.name,
    AirFreightAction.updated_at.name,
}

ACTION_PARAMS = [
    AirFreightRateStatistic.currency.name,
    AirFreightRateStatistic.rate_id.name,
    AirFreightRateStatistic.validity_id.name,
    AirFreightRateStatistic.validity_start.name,
    AirFreightRateStatistic.validity_end.name,
    # AirFreightRateStatistic.mode.name,
    AirFreightRateStatistic.source.name,
    # AirFreightRateStatistic.source_id.name,
    AirFreightRateStatistic.currency.name,
    AirFreightRateStatistic.price.name,
    AirFreightRateStatistic.standard_price.name,
    AirFreightRateStatistic.price.name,
    AirFreightRateStatistic.standard_price.name,
    AirFreightRateStatistic.rate_type.name,
    # AirFreightRateStatistic.market_price.name,
    AirFreightRateStatistic.airline_id.name,
    AirFreightRateStatistic.service_provider_id.name,
    AirFreightRateStatistic.origin_region_id.name,
    AirFreightRateStatistic.destination_region_id.name,
    AirFreightRateStatistic.performed_by_id.name,
    AirFreightRateStatistic.procured_by_id.name,
    AirFreightRateStatistic.sourced_by_id.name,
    # AirFreightRateStatistic.parent_mode.name,
    AirFreightRateStatistic.source.name,
    AirFreightRateStatistic.rate_created_at.name,
    AirFreightRateStatistic.rate_updated_at.name,
    AirFreightRateStatistic.validity_created_at.name,
    AirFreightRateStatistic.validity_updated_at.name,
]


class SpotSearch:
    def __init__(self) -> None:
        self.increment_keys = {AirFreightRateStatistic.spot_search_count.name}
        self.air_freight_rate_statistic = None
        self.common_params = dict()

    def set(self, params) -> None:
        covered_rates = set()
        for key in COMMON_PARAMS:
            self.common_params[key] = getattr(params, key)
            self.common_params["spot_search"] = 1
        if not params.rates:
            self.__create_action(self.common_params)
        for rate in params.rates:
            identifier = get_air_freight_identifier(rate.rate_id, rate.validity_id)
            if identifier in covered_rates:
                continue
            covered_rates.add(identifier)
            self.air_freight_rate_statistic = self.__get_air_freight_rate_statistic(
                rate.rate_id, rate.validity_id, identifier
            )
            if self.air_freight_rate_statistic is None:
                continue
            self.__update_statistics(dict(updated_at=params.updated_at))
            action_params = self.__get_action_params()
            self.__create_action(action_params)

    def __get_action_params(self) -> dict:
        action_params = {
            "air_freight_rate_statistic_id": self.air_freight_rate_statistic.id,
            **{
                k: getattr(self.air_freight_rate_statistic, k)
                for k in ACTION_PARAMS
                if getattr(self.air_freight_rate_statistic, k) is not None
            },
        }
        action_params.update(self.common_params)
        return action_params

    def __create_action(self, params) -> None:
        air_freight_action = (
            AirFreightAction.select(AirFreightAction.id)
            .where(
                # AirFreightAction.spot_search_id == params.get("spot_search_id"),
                AirFreightAction.rate_id == params.get("rate_id"),
                AirFreightAction.validity_id == params.get("validity_id"),
            )
            .first()
        )
        if air_freight_action is not None:
            return
        print(params, "paramsa")
        air_freight_action = AirFreightAction(**params)
        air_freight_action.save()

    def __get_air_freight_rate_statistic(
        self, rate_id, validity_id, identifier
    ) -> Union[None, Model]:
        air_freight_rate_statistic = (
            AirFreightRateStatistic.select()
            .where(AirFreightRateStatistic.identifier == identifier)
            .first()
        )
        if air_freight_rate_statistic is None:
            air_freight_rate_statistic = create_air_freight_rate_statistic_fallback(
                rate_id, validity_id
            )
        return air_freight_rate_statistic

    def __update_statistics(self, params) -> None:
        for key in self.increment_keys:
            setattr(
                self.air_freight_rate_statistic,
                key,
                getattr(self.air_freight_rate_statistic, key) + 1,
            )
        for key, value in params.items():
            setattr(self.air_freight_rate_statistic, key, value)
        self.air_freight_rate_statistic.save()
