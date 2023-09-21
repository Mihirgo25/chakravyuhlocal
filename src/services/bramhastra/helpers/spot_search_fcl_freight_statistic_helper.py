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
        for rate in self.rates:
            self.fcl_freight_rate_statistic = self.__get_fcl_freight_rate_statistic()
            if self.fcl_freight_rate_statistic is None:
                continue
            self.__update_statistics(dict(updated_at=params.updated_at))
            action_params = self.__get_action_params(rate, params)
            self.__create_action(action_params)

    def __get_action_params(self, rates, params) -> dict:
        action_params = {
            "spot_search_id": params.spot_search_id,
            "spot_search_fcl_freight_services_id": params.spot_search_fcl_freight_services_id,
            "spot_search": 1,
            **{
                k: getattr(self.fcl_freight_rate_statistic, k.name)
                for k in REQUIRED_ACTION_FIELDS
            },
            **rates,
        }
        return action_params

    def __create_action(self, params) -> None:
        FclFreightAction.create(**params)

    def __get_fcl_freight_rate_statistic(self, rate_dict) -> Union[None, Model]:
        identifier = get_fcl_freight_identifier(**rate_dict)
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
