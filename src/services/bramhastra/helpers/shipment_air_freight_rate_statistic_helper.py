from services.bramhastra.models.air_freight_rate_statistic import (
    AirFreightRateStatistic,
)
from services.bramhastra.models.shipment_air_freight_rate_statistic import (
    ShipmentAirFreightRateStatistic,
)
from services.bramhastra.models.air_freight_action import AirFreightAction
from services.bramhastra.constants import UNIQUE_AIR_SPOT_SEARCH_SERVICE_KEYS
from services.bramhastra.enums import ShipmentState, ShipmentAction
from services.bramhastra.helpers.common_statistic_helper import (
    get_air_freight_identifier,
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
        print(self.request.air_freight_services, 'gg')
        for air_freight_service in self.request.air_freight_services:
            shipment_copy = shipment.copy()
            shipment_copy.update(air_freight_service.dict())
            unique_air_spot_search_service_key = (
                self.__get_unique_air_spot_search_service_key(air_freight_service)
            )
            action = actions.get(unique_air_spot_search_service_key)
            print(action, 'llll')
            if action is not None:
                action_update_params = shipment_copy.copy()
                action_update_params[
                    AirFreightAction.bas_standard_price_accuracy.name
                ] = 100
                self.__update(
                    action,
                    {AirFreightAction.shipment.name},
                    action_update_params,
                )
            statistic = (
                AirFreightRateStatistic.select()
                .where(
                    AirFreightRateStatistic.id == action.air_freight_rate_statistic_id
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
                        "air_freight_rate_statistic_id": statistic.id,
                    }
                )
                self.__create(ShipmentAirFreightRateStatistic, shipment_copy)

    def __get_unique_air_spot_search_service_key(self, model):
        return "".join(
            [str(getattr(model, key)) for key in UNIQUE_AIR_SPOT_SEARCH_SERVICE_KEYS]
        )

    def __create(self, model, params):
        model.create(**params)

    def __get_actions(self, source_id):
        actions = AirFreightAction.select().where(
            AirFreightAction.checkout_id == source_id
        )
        actions_hash = dict()
        for action in actions:
            unique_air_spot_search_service_key = (
                self.__get_unique_air_spot_search_service_key(action)
            )
            actions_hash[unique_air_spot_search_service_key] = action
        return actions_hash

    def update(self):
        params = self.request.dict(
            exclude={
                AirFreightAction.shipment_id.name,
                AirFreightAction.shipment_service_id.name,
            },
            exclude_none=True,
        )
        if AirFreightAction.shipment_state.name in params:
            shipment_state = self.__get_shipment_state_bool_string(
                params.get(AirFreightAction.shipment_state.name)
            )
            params["shipment_state"] = params.get(AirFreightAction.shipment_state.name)
        rates = (
            AirFreightAction.update(**params)
            .where(AirFreightAction.shipment_id == self.request.shipment_id)
            .returning(AirFreightAction.rate_id, AirFreightAction.validity_id)
            .execute()
        )
        for rate in rates:
            air_freight_rate_statistic = (
                AirFreightRateStatistic.select()
                .where(
                    AirFreightRateStatistic.identifier
                    == get_air_freight_identifier(rate.rate_id, rate.validity_id)
                )
                .first()
            )
            if shipment_state not in {"shipment_completed", "shipment_cancelled"}:
                continue
            setattr(
                air_freight_rate_statistic,
                shipment_state,
                getattr(air_freight_rate_statistic, shipment_state) + 1,
            )
            try:
                air_freight_rate_statistic.save()
            except:
                pass

    def update_service(self) -> None:
        params = self.request.dict(
            exclude={
                AirFreightAction.shipment_service_id.name,
            },
            exclude_none=True,
        )
        AirFreightAction.update(**params).where(
            AirFreightAction.shipment_service_id == self.request.shipment_service_id
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
