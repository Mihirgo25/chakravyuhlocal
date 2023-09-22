from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)
from services.bramhastra.models.shipment_fcl_freight_rate_statistic import (
    ShipmentFclFreightRateStatistic,
)
from services.bramhastra.models.fcl_freight_action import FclFreightAction
from services.bramhastra.constants import UNIQUE_FCL_SPOT_SEARCH_SERVICE_KEYS


class Shipment:
    def __init__(self, request) -> None:
        self.request = request

    def set(self):
        shipment = self.request.dict(include={"shipment"})["shipment"]
        actions = self.__get_actions(self.request.shipment.shipment_source_id)
        for fcl_freight_service in self.request.fcl_freight_services:
            shipment_copy = shipment.copy()
            shipment_copy.update(fcl_freight_service.dict())
            unique_fcl_spot_search_service_key = (
                self.get_unique_fcl_spot_search_service_key(fcl_freight_service)
            )
            action = actions.get(unique_fcl_spot_search_service_key)
            if action is not None:
                action_update_params = shipment_copy.copy()
                action_update_params["bas_standard_accuracy"] = 100
                self.__update(
                    action, {FclFreightAction.shipment.name}, action_update_params
                )
            statistic = (
                FclFreightRateStatistic.select()
                .where(
                    FclFreightRateStatistic.id == action.fcl_freight_rate_statistic_id
                )
                .first()
            )
            if statistic is not None:
                self.__update(
                    statistic,
                    {
                        "bookings_created",
                        shipment_copy.get("shipment_state")
                        if shipment_copy.get("shipment_state") in {"shipment_recieved"}
                        else f"shipment_{shipment_copy.get('shipment_state')}",
                    },
                )
                shipment_copy.update(
                    {
                        "rate_id": statistic.rate_id,
                        "validity_id": statistic.validity_id,
                        "fcl_freight_rate_statistic_id": statistic.id,
                        "shipment_serial_id": 34,
                    }
                )
                self.create(ShipmentFclFreightRateStatistic, shipment_copy)

    def get_unique_fcl_spot_search_service_key(self, model):
        return "".join(
            [str(getattr(model, key)) for key in UNIQUE_FCL_SPOT_SEARCH_SERVICE_KEYS]
        )

    def create(self, model, params):
        model.create(**params)

    def __get_actions(self, checkout_id):
        actions = FclFreightAction.select().where(
            FclFreightAction.checkout_id == checkout_id
        )
        actions_hash = dict()
        for action in actions:
            unique_fcl_spot_search_service_key = (
                self.get_unique_fcl_spot_search_service_key(action)
            )
            actions_hash[unique_fcl_spot_search_service_key] = action
        return actions_hash

    def update(self):
        params = self.request.shipment.dicts(
            exclude={
                FclFreightAction.shipment_id.name,
                FclFreightAction.shipment_service_id.name,
            },
            exclude_none=True,
        )
        FclFreightAction.update(**params).where(
            FclFreightAction.shipment_id == self.request.shipment_id
        ).execute()

    def __update(self, model, increment_keys: set = None, params: dict = None):
        if increment_keys is not None:
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
