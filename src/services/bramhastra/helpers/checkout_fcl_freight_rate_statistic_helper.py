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
        pass

    def set(self, params):
        actions = self.get_actions(params.checkout_source_id)
        for checkout_fcl_freight_service in params.checkout_fcl_freight_services:
            fcl_freight_rate_statistic = self.get_fcl_freight_rate_statistic(
                checkout_fcl_freight_service.rate
            )
            if fcl_freight_rate_statistic is None:
                continue
            self.update_statistics(
                fcl_freight_rate_statistic,
                params=dict(updated_at=params.created_at),
            )
            unique_fcl_spot_search_service_key = (
                self.get_unique_fcl_spot_search_service_key(fcl_freight_rate_statistic)
            )
            action = actions.get(unique_fcl_spot_search_service_key)

            action_update_params = {
                "checkout_source": params.checkout_source,
                "updated_at": params.created_at,
                "checkout_id": checkout_fcl_freight_service.checkout_id,
                "checkout": 1,
                "checkout_created_at": params.created_at,
                "checkout_fcl_freight_service_id": checkout_fcl_freight_service.checkout_fcl_freight_service_id,
            }
            if action is not None:
                self.update(action, action_update_params)

    def get_fcl_freight_rate_statistic(self, rate):
        return (
            FclFreightRateStatistic.select()
            .where(
                FclFreightRateStatistic.identifier
                == get_fcl_freight_identifier(rate.rate_id, rate.validity_id)
            )
            .first()
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
        if params is None:
            return
        for key, value in params.items():
            if value is not None:
                setattr(model, key, value)
        model.save()

    def update_statistics(
        self,
        model,
        params=None,
        increment_keys: set = {FclFreightRateStatistic.checkout_count.name},
    ):
        for key in increment_keys:
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
