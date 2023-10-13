from services.bramhastra.helpers.common_statistic_helper import (
    get_fcl_freight_identifier,
    create_fcl_freight_rate_statistic_fallback,
)
from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)
from services.bramhastra.models.fcl_freight_action import FclFreightAction
from typing import Union
from peewee import Model

COMMON_PARAMS = {
    FclFreightAction.spot_search_fcl_freight_service_id.name,
    FclFreightAction.spot_search_id.name,
    FclFreightAction.origin_port_id.name,
    FclFreightAction.destination_port_id.name,
    FclFreightAction.origin_main_port_id.name,
    FclFreightAction.destination_main_port_id.name,
    FclFreightAction.origin_country_id.name,
    FclFreightAction.destination_country_id.name,
    FclFreightAction.origin_continent_id.name,
    FclFreightAction.destination_continent_id.name,
    FclFreightAction.origin_trade_id.name,
    FclFreightAction.destination_trade_id.name,
    FclFreightAction.container_size.name,
    FclFreightAction.container_type.name,
    FclFreightAction.containers_count.name,
    FclFreightAction.commodity.name,
    FclFreightAction.created_at.name,
    FclFreightAction.updated_at.name,
}

ACTION_PARAMS = [
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
    FclFreightRateStatistic.bas_currency.name,
]


class SpotSearch:
    def __init__(self) -> None:
        self.increment_keys = {FclFreightRateStatistic.spot_search_count.name}
        self.fcl_freight_rate_statistic = None
        self.common_params = dict()

    def set(self, params) -> None:
        covered_rates = set()
        for key in COMMON_PARAMS:
            self.common_params[key] = getattr(params, key)
            self.common_params["spot_search"] = 1
        if not params.rates:
            self.__create_action(self.common_params)
        for rate in params.rates:
            identifier = get_fcl_freight_identifier(rate.rate_id, rate.validity_id)
            if identifier in covered_rates:
                continue
            covered_rates.add(identifier)
            self.fcl_freight_rate_statistic = self.__get_fcl_freight_rate_statistic(
                rate.rate_id, rate.validity_id, identifier
            )
            if self.fcl_freight_rate_statistic is None:
                continue
            self.__update_statistics(dict(updated_at=params.updated_at))
            action_params = self.__get_action_params()
            self.__create_action(action_params)

    def __get_action_params(self) -> dict:
        action_params = {
            "fcl_freight_rate_statistic_id": self.fcl_freight_rate_statistic.id,
            **{
                k: getattr(self.fcl_freight_rate_statistic, k)
                for k in ACTION_PARAMS
                if getattr(self.fcl_freight_rate_statistic, k) is not None
            },
        }
        action_params.update(self.common_params)
        return action_params

    def __create_action(self, params) -> None:
        fcl_freight_action = (
            FclFreightAction.select(FclFreightAction.id)
            .where(
                FclFreightAction.spot_search_id == params.get("spot_search_id"),
                FclFreightAction.rate_id == params.get("rate_id"),
                FclFreightAction.validity_id == params.get("validity_id"),
            )
            .first()
        )
        if fcl_freight_action is not None:
            return
        print(params, "paramsa")
        fcl_freight_action = FclFreightAction(**params)
        fcl_freight_action.save()

    def __get_fcl_freight_rate_statistic(
        self, rate_id, validity_id, identifier
    ) -> Union[None, Model]:
        fcl_freight_rate_statistic = (
            FclFreightRateStatistic.select()
            .where(FclFreightRateStatistic.identifier == identifier)
            .first()
        )
        if fcl_freight_rate_statistic is None:
            fcl_freight_rate_statistic = create_fcl_freight_rate_statistic_fallback(
                rate_id, validity_id
            )
        return fcl_freight_rate_statistic

    def __update_statistics(self, params) -> None:
        for key in self.increment_keys:
            setattr(
                self.fcl_freight_rate_statistic,
                key,
                getattr(self.fcl_freight_rate_statistic, key) + 1,
            )
        for key, value in params.items():
            setattr(self.fcl_freight_rate_statistic, key, value)
        self.fcl_freight_rate_statistic.save()
