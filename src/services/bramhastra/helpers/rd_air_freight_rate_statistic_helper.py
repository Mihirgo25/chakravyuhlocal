from services.bramhastra.models.air_freight_rate_statistic import (
    AirFreightRateStatistic,
)
from services.bramhastra.helpers.common_statistic_helper import (
    get_air_freight_identifier,
)
from peewee import Model
from services.bramhastra.models.air_freight_action import AirFreightAction
from services.bramhastra.models.shipment_air_freight_rate_statistic import (
    ShipmentAirFreightRateStatistic,
)
from services.bramhastra.enums import SelectTypes, RevenueDeskState

RATE_KEYS = {
    AirFreightRateStatistic.rate_id.name,
    AirFreightRateStatistic.validity_id.name,
    AirFreightRateStatistic.standard_price.name,
}

SELECTED_RATE_KEYS = {
    AirFreightAction.rate_id.name,
    AirFreightAction.validity_id.name,
    AirFreightAction.selected_air_freight_rate_statistic_id.name,
    AirFreightAction.selected_standard_price.name,
}

STATISTICS_KEYS = {
    AirFreightAction.standard_price_accuracy.name,
    AirFreightAction.standard_price_diff_from_selected_rate.name,
}


class RevenueDesk:
    def __init__(self, init=False) -> None:
        if not init:
            return
        self.selected_rate = dict()
        self.original_rate = dict()
        self.original_rate_numerics = dict()
        self.selected_rate_numerics = dict()

    def update_rd_visit_count(self, request) -> None:
        common_update_params = {
            "updated_at": request.created_at,
        }
        action_updated = False
        for validity_id in request.validities:
            Air_freight_rate_statistic = (
                AirFreightRateStatistic.select()
                .where(
                    AirFreightRateStatistic.identifier
                    == get_air_freight_identifier(request.rate_id, validity_id)
                )
                .first()
            )
            if Air_freight_rate_statistic:
                statistic_increment_keys = {
                    AirFreightRateStatistic.revenue_desk_visit_count.name
                }
                self.update_foreign_reference(
                    Air_freight_rate_statistic,
                    statistic_increment_keys,
                    common_update_params,
                )
            Air_freight_action = (
                AirFreightAction.select()
                .where(
                    AirFreightAction.shipment_service_id
                    == request.shipment_service_id
                )
                .first()
            )
            if (Air_freight_action is not None) and not action_updated:
                self.set_revenue_desk_visit_state(Air_freight_action, "visited")
                self.update_foreign_reference(
                    Air_freight_action, None, common_update_params
                )
                action_updated = True

    def update_foreign_reference(
        self, model: Model, increment_keys: set = None, params: dict = None
    ) -> None:
        if increment_keys:
            for key in increment_keys:
                setattr(model, key, getattr(model, key) + 1)
        if params:
            for k, v in params.items():
                if v is not None:
                    setattr(model, k, v)
        model.save()

    def set_revenue_desk_visit_state(self, model: Model, state: str = "empty") -> None:
        setattr(
            model,
            AirFreightAction.revenue_desk_state.name,
            getattr(RevenueDeskState, state).name,
        )

    def update_selected_for_preference_count(self, request) -> None:
        common_update_params = {
            "updated_at": request.created_at,
            "given_priority": request.selected_for_preference.given_priority,
        }
        Air_freight_rate_statistic = (
            AirFreightRateStatistic.select()
            .where(
                AirFreightRateStatistic.identifier
                == get_air_freight_identifier(
                    request.selected_for_preference.rate_id,
                    request.selected_for_preference.validity_id,
                )
            )
            .first()
        )
        if Air_freight_rate_statistic is not None:
            statistic_increment_keys = {AirFreightRateStatistic.so1_visit_count.name}
            self.update_foreign_reference(
                Air_freight_rate_statistic,
                statistic_increment_keys,
                common_update_params,
            )
        Air_freight_action = (
            AirFreightAction.select()
            .where(
                AirFreightAction.shipment_service_id
                == request.shipment_service_id
            )
            .first()
        )
        if Air_freight_action is not None:
            self.set_revenue_desk_visit_state(
                Air_freight_action, "selected_for_preference"
            )
            self.update_foreign_reference(
                Air_freight_action, None, common_update_params
            )

    def set_statistics(self) -> None:
        for key in STATISTICS_KEYS:
            eval(f"self.set_{key}(key)")

    def set_standard_price_accuracy(self, key: str) -> None:
        self.original_rate_numerics[key] = (
            (
                self.original_rate[AirFreightAction.standard_price.name]
                / (self.selected_rate[AirFreightAction.standard_price.name] or 1)
            )
            - 1
        ) * 100
        self.selected_rate_numerics[key] = 100

    def set_standard_price_diff_from_selected_rate(self, key: str) -> None:
        self.original_rate_numerics[key] = (
            self.original_rate[AirFreightAction.standard_price.name]
            - self.selected_rate[AirFreightAction.standard_price.name]
        )

    def set(self, request) -> None:
        self.common_update_params = {"updated_at": request.created_at}
        selected_statistic = (
            AirFreightRateStatistic.select()
            .where(
                AirFreightRateStatistic.identifier
                == get_air_freight_identifier(
                    request.selected_for_booking.rate_id,
                    request.selected_for_booking.validity_id,
                )
            )
            .first()
        )
        original_action = (
            AirFreightAction.select()
            .where(
                AirFreightAction.shipment_service_id
                == request.shipment_service_id
            )
            .first()
        )
        original_statistic = (
            AirFreightRateStatistic.select()
            .where(
                AirFreightRateStatistic.identifier
                == get_air_freight_identifier(
                    original_action.rate_id, original_action.validity_id
                )
            )
            .first()
        )
        if not (original_statistic or selected_statistic):
            return
        self.update_shipment(
            request.shipment_service_id, selected_statistic
        )
        for key in RATE_KEYS:
            self.selected_rate[key] = getattr(selected_statistic, key)
            self.original_rate[key] = getattr(original_statistic, key)
        self.set_statistics()
        self.selected_rate_numerics.update(
            {
                AirFreightAction.selected_air_freight_rate_statistic_id.name: selected_statistic.id,
                AirFreightAction.rate_id.name: selected_statistic.rate_id,
                AirFreightAction.validity_id.name: selected_statistic.validity_id,
                AirFreightAction.selected_standard_price.name: selected_statistic.standard_price,
            }
        )
        self.update_foreign_reference(
            selected_statistic,
            {AirFreightRateStatistic.so1_select_count.name},
            self.selected_rate_numerics,
        )
        self.update_foreign_reference(
            original_statistic, None, self.original_rate_numerics
        )
        self.set_revenue_desk_visit_state(original_action, "selected_for_booking")

        for key in SELECTED_RATE_KEYS:
            self.original_rate_numerics[key] = getattr(selected_statistic, key)

        self.original_rate_numerics[
            AirFreightAction.selected_type.name
        ] = SelectTypes.SO1.value

        self.update_foreign_reference(
            original_action,
            None,
            self.original_rate_numerics,
        )

    def update_shipment(self, shipment_service_id, statistic):
        ShipmentAirFreightRateStatistic.update(
            rate_id=statistic.rate_id, validity_id=statistic.validity_id
        ).where(
            ShipmentAirFreightRateStatistic.shipment_service_id == shipment_service_id
        )
