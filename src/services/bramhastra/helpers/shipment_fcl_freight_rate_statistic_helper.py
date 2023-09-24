from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)
from services.bramhastra.models.shipment_fcl_freight_rate_statistic import (
    ShipmentFclFreightRateStatistic,
)
from services.bramhastra.models.fcl_freight_action import FclFreightAction
from services.bramhastra.constants import UNIQUE_FCL_SPOT_SEARCH_SERVICE_KEYS
from services.bramhastra.enums import ShipmentState, ShipmentAction


class Shipment:
    def __init__(self, request) -> None:
        self.request = (
            request.params
            if request.action == ShipmentAction.create.value
            else request.shipment_update_params
        )

    def __get_shipment_state_bool_string(self, shipment_state) -> str:
        if shipment_state in {ShipmentState.shipment_received.value}:
            return shipment_state
        return f"shipment_{shipment_state}"

    def set(self):
        shipment = self.request.dict(include={"shipment"})["shipment"]
        actions = self.__get_actions(self.request.shipment.shipment_source_id)
        for fcl_freight_service in self.request.fcl_freight_services:
            shipment_copy = shipment.copy()
            shipment_copy.update(fcl_freight_service.dict())
            unique_fcl_spot_search_service_key = (
                self.get_unique_fcl_spot_search_service_key(fcl_freight_service)
            )
            shipment_state = self.__get_shipment_state_bool_string(
                shipment_copy.get(FclFreightAction.shipment_state.name)
            )
            action = actions.get(unique_fcl_spot_search_service_key)
            if action is not None:
                action_update_params = shipment_copy.copy()
                action_update_params[
                    FclFreightAction.bas_standard_price_accuracy.name
                ] = 100
                action_update_params[shipment_state] = 1
                self.__update(
                    action,
                    {FclFreightAction.shipment.name, shipment_state},
                    action_update_params,
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
                    },
                )
                shipment_copy.update(
                    {
                        "rate_id": statistic.rate_id,
                        "validity_id": statistic.validity_id,
                        "fcl_freight_rate_statistic_id": statistic.id,
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
        params = self.request.dict(
            exclude={
                FclFreightAction.shipment_id.name,
                FclFreightAction.shipment_service_id.name,
            },
            exclude_none=True,
        )
        if FclFreightAction.shipment_state.name in params:
            shipment_state = self.__get_shipment_state_bool_string(
                params.get(FclFreightAction.shipment_state.name)
            )
            params[shipment_state] = 1
        FclFreightAction.update(**params).where(
            FclFreightAction.shipment_id == self.request.shipment_id
        ).execute()

    def update_service(self) -> None:
        params = self.request.dict(
            exclude={
                FclFreightAction.shipment_service_id.name,
            },
            exclude_none=True,
        )
        FclFreightAction.update(**params).where(
            FclFreightAction.shipment_serial_id == self.request.shipment_service_id
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
