from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)
from services.bramhastra.models.shipment_fcl_freight_rate_statistic import (
    ShipmentFclFreightRateStatistic,
)
from services.bramhastra.models.fcl_freight_action import FclFreightAction
from services.bramhastra.constants import UNIQUE_FCL_SPOT_SEARCH_SERVICE_KEYS
from services.bramhastra.enums import ShipmentState, ShipmentAction
from services.bramhastra.helpers.common_statistic_helper import (
    get_fcl_freight_identifier,
)


class Shipment:
    def __init__(self, request) -> None:
        if request.action == ShipmentAction.create.value:
            self.request = request.params
        elif request.shipment_update_params:
            self.request = request.shipment_update_params
        elif request.shipment_service_update_params:
            self.request = request.shipment_service_update_params

    def __get_shipment_state_bool_string(self, shipment_state) -> str:
        if shipment_state == "shipment_received":
            return shipment_state
        return f"shipment_{shipment_state}"

    def set(self):
        shipment = self.request.dict(include={"shipment"})["shipment"]
        actions = self.__get_actions(
            self.request.checkout_id or self.request.shipment.shipment_source_id
        )
        print(actions, shipment, "actions")
        if not actions:
            return
        print(self.request.fcl_freight_services, 'gg')
        for fcl_freight_service in self.request.fcl_freight_services:
            shipment_copy = shipment.copy()
            shipment_copy.update(fcl_freight_service.dict())
            unique_fcl_spot_search_service_key = (
                self.__get_unique_fcl_spot_search_service_key(fcl_freight_service)
            )
            action = actions.get(unique_fcl_spot_search_service_key)
            print(action, 'llll')
            if action is not None:
                action_update_params = shipment_copy.copy()
                action_update_params[
                    FclFreightAction.bas_standard_price_accuracy.name
                ] = 100
                self.__update(
                    action,
                    {FclFreightAction.shipment.name},
                    action_update_params,
                )
            statistic = (
                FclFreightRateStatistic.select()
                .where(
                    FclFreightRateStatistic.id == action.fcl_freight_rate_statistic_id
                )
                .first()
            )
            print(statistic, 'statistic')
            if statistic is not None:
                self.__update(
                    statistic,
                    {"bookings_created"},
                    {"last_shipment_booked_at": shipment["shipment_created_at"]},
                )
                shipment_copy.update(
                    {
                        "rate_id": statistic.rate_id,
                        "validity_id": statistic.validity_id,
                        "fcl_freight_rate_statistic_id": statistic.id,
                    }
                )
                self.__create(ShipmentFclFreightRateStatistic, shipment_copy)

    def __get_unique_fcl_spot_search_service_key(self, model):
        return "".join(
            [str(getattr(model, key)) for key in UNIQUE_FCL_SPOT_SEARCH_SERVICE_KEYS]
        )

    def __create(self, model, params):
        model.create(**params)

    def __get_actions(self, source_id):
        actions = FclFreightAction.select().where(
            FclFreightAction.checkout_id == source_id
        )
        actions_hash = dict()
        for action in actions:
            unique_fcl_spot_search_service_key = (
                self.__get_unique_fcl_spot_search_service_key(action)
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
            params["shipment_state"] = params.get(FclFreightAction.shipment_state.name)
        rates = (
            FclFreightAction.update(**params)
            .where(FclFreightAction.shipment_id == self.request.shipment_id)
            .returning(FclFreightAction.rate_id, FclFreightAction.validity_id)
            .execute()
        )
        for rate in rates:
            fcl_freight_rate_statistic = (
                FclFreightRateStatistic.select()
                .where(
                    FclFreightRateStatistic.identifier
                    == get_fcl_freight_identifier(rate.rate_id, rate.validity_id)
                )
                .first()
            )
            if shipment_state not in {"shipment_completed", "shipment_cancelled"}:
                continue
            setattr(
                fcl_freight_rate_statistic,
                shipment_state,
                getattr(fcl_freight_rate_statistic, shipment_state) + 1,
            )
            try:
                fcl_freight_rate_statistic.save()
            except:
                pass

    def update_service(self) -> None:
        params = self.request.dict(
            exclude={
                FclFreightAction.shipment_service_id.name,
            },
            exclude_none=True,
        )
        FclFreightAction.update(**params).where(
            FclFreightAction.shipment_service_id == self.request.shipment_service_id
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
