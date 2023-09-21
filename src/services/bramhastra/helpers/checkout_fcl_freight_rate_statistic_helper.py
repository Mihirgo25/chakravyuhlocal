from services.bramhastra.helpers.common_statistic_helper import (
    get_fcl_freight_identifier,
)
from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)
from services.bramhastra.models.fcl_freight_action import FclFreightAction
from services.bramhastra.constants import UNIQUE_FCL_SPOT_SEARCH_SERVICE_KEYS


class Checkout:
    def __init__(self) -> None:
        self.increment_keys = {FclFreightRateStatistic.checkout_count.name}

    def set(self, params):
        actions = self.get_actions_dict(params.source_id)
        for checkout_fcl_freight_service in params.checkout_fcl_freight_services:
            fcl_freight_rate_statistic = self.get_fcl_freight_rate_statistic(
                checkout_fcl_freight_service.rate
            )
            self.update_statistics(
                fcl_freight_rate_statistic,
                dict(created_at=params.created_at, source=params.source),
            )
            unique_fcl_spot_search_service_key = (
                self.get_unique_fcl_spot_search_service_key(fcl_freight_rate_statistic)
            )
            action = actions.get(unique_fcl_spot_search_service_key)
            action_update_params = params.dict(
                include={"checkout_source", "created_at"}
            )
            action_update_params[
                "checkout_id"
            ] = checkout_fcl_freight_service.checkout_id
            if action is not None:
                self.update(action, action_update_params)

    def get_fcl_freight_rate_statistic(self, rate):
        FclFreightRateStatistic.select().where(
            FclFreightRateStatistic.identifier
            == get_fcl_freight_identifier(rate.rate_id, rate.validity_id)
        )

    def get_unique_fcl_spot_search_service_key(self, model):
        return "".join(
            [str(getattr(model, key)) for key in UNIQUE_FCL_SPOT_SEARCH_SERVICE_KEYS]
        )

    def get_actions(self, spot_search_id):
        actions = FclFreightAction.select().where(
            FclFreightAction.spot_search_id == spot_search_id
        )
        actions_hash = dict()
        for action in actions:
            unique_fcl_spot_search_service_key = (
                self.get_unique_fcl_spot_search_service_key(action)
            )
            actions_hash[unique_fcl_spot_search_service_key] = action
        return actions_hash

    def update(self, model, params):
        for key, value in params.items():
            if value is not None:
                setattr(model, key, value)

    def update_statistics(self, model, params=None):
        for key in self.increment_keys:
            setattr(
                model,
                key,
                getattr(model, key) + 1,
            )
        if params is not None:
            for key, value in params.items():
                if value is not None:
                    setattr(model, key, value)
        model.save()
