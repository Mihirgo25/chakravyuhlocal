from services.bramhastra.helpers.common_statistic_helper import (
    get_fcl_freight_identifier,
)
from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)
from services.bramhastra.models.fcl_freight_action import FclFreightAction
from services.bramhastra.helpers.common_statistic_helper import REQUIRED_ACTION_FIELDS
from typing import Union
from peewee import Model


class SpotSearch:
    def __init__(self) -> None:
        self.increment_keys = {FclFreightRateStatistic.spot_search_count.name}
        self.fcl_freight_rate_statistic = None

    def set(self, params) -> None:
        covered_rates = set()
        for rate in params.rates:
            identifier = get_fcl_freight_identifier(rate.rate_id, rate.validity_id)
            if identifier in covered_rates:
                continue
            covered_rates.add(identifier)
            self.fcl_freight_rate_statistic = self.__get_fcl_freight_rate_statistic(
                identifier
            )
            if self.fcl_freight_rate_statistic is None:
                continue
            self.__update_statistics(dict(updated_at=params.updated_at))
            action_params = self.__get_action_params(params)
            self.__create_action(action_params)

    def __get_action_params(self, params) -> dict:
        action_params = {
            "spot_search_id": params.spot_search_id,
            "spot_search_fcl_freight_service_id": params.spot_search_fcl_freight_services_id,
            "spot_search": 1,
            "fcl_freight_rate_statistic_id": self.fcl_freight_rate_statistic.id,
            **{
                k: getattr(self.fcl_freight_rate_statistic, k)
                for k in REQUIRED_ACTION_FIELDS
                if getattr(self.fcl_freight_rate_statistic, k) is not None
            },
        }
        return action_params

    def __create_action(self, params) -> None:
        fcl_freight_action = FclFreightAction(**params)
        fcl_freight_action.save()

    def __get_fcl_freight_rate_statistic(self, identifier) -> Union[None, Model]:
        return (
            FclFreightRateStatistic.select()
            .where(FclFreightRateStatistic.identifier == identifier)
            .first()
        )

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
