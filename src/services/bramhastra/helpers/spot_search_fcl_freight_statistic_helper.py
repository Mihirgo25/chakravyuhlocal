from services.bramhastra.models.spot_search_fcl_freight_rate_statistic import (
    SpotSearchFclFreightRateStatistic,
)
from services.bramhastra.helpers.common_statistic_helper import (
    get_fcl_freight_identifier,
)
from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)
from services.bramhastra.models.fcl_freight_action import FclFreightAction
from services.bramhastra.helpers.common_statistic_helper import REQUIRED_ACTION_FIELDS


class SpotSearch:
    def __init__(self, params) -> None:
        self.common_param = params.dict(exclude={"rates"})
        self.spot_search_id = params.spot_search_id
        self.spot_search_params = []
        self.rates = params.rates
        self.increment_keys = {"spot_search_count"}
        self.fcl_freight_rate_statistic = None

    def set(self):
        for rate in self.rates:
            param = self.common_param.copy()
            rate_dict = rate.dict(exclude={"payment_term", "schedule_type"})
            param.update(rate_dict)
            self.fcl_freight_rate_statistic = (
                FclFreightRateStatistic.select()
                .where(
                    FclFreightRateStatistic.identifier
                    == get_fcl_freight_identifier(**rate_dict)
                )
                .first()
            )
            if self.fcl_freight_rate_statistic is None:
                continue
            self.update_statistics(dict(updated_at=param["updated_at"]))
            if self.fcl_freight_rate_statistic:
                param[
                    "fcl_freight_rate_statistic_id"
                ] = self.fcl_freight_rate_statistic.id
                self.spot_search_params.append(param)
            fcl_freight_action_create_params = rate_dict
            fcl_freight_action_create_params["spot_search_id"] = self.spot_search_id
            fcl_freight_action_create_params.update(
                {
                    k: getattr(self.fcl_freight_rate_statistic, k.name)
                    for k in REQUIRED_ACTION_FIELDS
                }
            )
            self.create_action(fcl_freight_action_create_params)

    def create_action(self, params) -> None:
        FclFreightAction.create(**params)

    def update_statistics(self, params) -> None:
        for k in self.increment_keys:
            setattr(
                self.fcl_freight_rate_statistic,
                k,
                getattr(self.fcl_freight_rate_statistic, k) + 1,
            )
        for key, value in params.items():
            setattr(self.fcl_freight_rate_statistic, key, value)

        self.fcl_freight_rate_statistic.save()

    def create(self) -> int:
        return SpotSearchFclFreightRateStatistic.insert_many(
            self.spot_search_params
        ).execute()
