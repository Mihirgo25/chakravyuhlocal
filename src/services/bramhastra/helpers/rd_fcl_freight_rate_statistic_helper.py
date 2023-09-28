from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)
from services.bramhastra.helpers.common_statistic_helper import (
    get_fcl_freight_identifier,
)
from peewee import Model
from services.bramhastra.models.fcl_freight_action import FclFreightAction
from services.bramhastra.models.shipment_fcl_freight_rate_statistic import (
    ShipmentFclFreightRateStatistic,
)
from services.bramhastra.enums import SelectTypes
from services.bramhastra.enums import RevenueDeskState

RATE_KEYS = {
    FclFreightRateStatistic.rate_id.name,
    FclFreightRateStatistic.validity_id.name,
    FclFreightRateStatistic.bas_standard_price.name,
}

STATISTICS_KEYS = {
    FclFreightAction.bas_standard_price_accuracy.name,
    FclFreightAction.bas_standard_price_diff_from_selected_rate.name,
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
        for validity_id in request.validities:
            fcl_freight_rate_statistic = (
                FclFreightRateStatistic.select()
                .where(
                    FclFreightRateStatistic.identifier
                    == get_fcl_freight_identifier(request.rate_id, validity_id)
                )
                .first()
            )
            if fcl_freight_rate_statistic:
                statistic_increment_keys = {
                    FclFreightRateStatistic.revenue_desk_visit_count.name
                }
                self.update_foreign_reference(
                    fcl_freight_rate_statistic,
                    statistic_increment_keys,
                    common_update_params,
                )
            fcl_freight_action = (
                FclFreightAction.select()
                .where(
                    FclFreightAction.shipment_service_id
                    == request.shipment_fcl_freight_service_id
                )
                .first()
            )
            if fcl_freight_action:
                self.set_revenue_desk_visit_state(fcl_freight_action, "visited")
                self.update_foreign_reference(
                    fcl_freight_action, None, common_update_params
                )

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
            FclFreightAction.revenue_desk_state.name,
            getattr(RevenueDeskState, state).name,
        )

    def update_selected_for_preference_count(self, request) -> None:
        common_update_params = {
            "updated_at": request.created_at,
        }
        fcl_freight_rate_statistic = (
            FclFreightRateStatistic.select()
            .where(
                FclFreightRateStatistic.identifier
                == get_fcl_freight_identifier(
                    request.selected_for_preference.rate_id,
                    request.selected_for_preference.validity_id,
                )
            )
            .first()
        )
        if fcl_freight_rate_statistic is not None:
            statistic_increment_keys = {FclFreightRateStatistic.so1_visit_count.name}
            self.update_foreign_reference(
                fcl_freight_rate_statistic,
                statistic_increment_keys,
                common_update_params,
            )
        fcl_freight_action = (
            FclFreightAction.select()
            .where(
                FclFreightAction.shipment_service_id
                == request.shipment_fcl_freight_service_id
            )
            .first()
        )
        if fcl_freight_action is not None:
            self.set_revenue_desk_visit_state(
                fcl_freight_action, "selected_for_preference"
            )
            self.update_foreign_reference(
                fcl_freight_action, None, common_update_params
            )

    def set_statistics(self) -> None:
        for key in STATISTICS_KEYS:
            eval(f"self.set_{key}(key)")

    def set_bas_standard_price_accuracy(self, key: str) -> None:
        self.original_rate_numerics[key] = (
            1
            - (
                self.original_rate[FclFreightAction.bas_standard_price.name]
                / (self.selected_rate[FclFreightAction.bas_standard_price.name] or 1)
            )
        ) * 100
        self.selected_rate_numerics[key] = 100

    def set_bas_standard_price_diff_from_selected_rate(self, key: str) -> None:
        self.original_rate_numerics[key] = (
            self.original_rate[FclFreightAction.bas_standard_price.name]
            - self.selected_rate[FclFreightAction.bas_standard_price.name]
        )

    def set(self, request) -> None:
        self.common_update_params = {"updated_at": request.created_at}
        selected_statistic = (
            FclFreightRateStatistic.select()
            .where(
                FclFreightRateStatistic.identifier
                == get_fcl_freight_identifier(
                    request.selected_for_booking.rate_id,
                    request.selected_for_booking.validity_id,
                )
            )
            .first()
        )
        original_action = (
            FclFreightAction.select()
            .where(
                FclFreightAction.shipment_service_id
                == request.shipment_fcl_freight_service_id
            )
            .first()
        )
        original_statistic = (
            FclFreightRateStatistic.select()
            .where(
                FclFreightRateStatistic.identifier
                == get_fcl_freight_identifier(
                    original_action.rate_id, original_action.validity_id
                )
            )
            .first()
        )
        if not (original_statistic or selected_statistic):
            return
        self.update_shipment(
            request.shipment_fcl_freight_service_id, selected_statistic
        )
        for key in RATE_KEYS:
            self.selected_rate[key] = getattr(selected_statistic, key)
            self.original_rate[key] = getattr(original_statistic, key)
        self.set_statistics()
        self.selected_rate_numerics.update(
            {
                FclFreightAction.selected_fcl_freight_rate_statistic_id.name: selected_statistic.id,
                FclFreightAction.selected_rate_id.name: selected_statistic.rate_id,
                FclFreightAction.selected_validity_id.name: selected_statistic.validity_id,
                FclFreightAction.selected_bas_standard_price.name: selected_statistic.bas_standard_price,
            }
        )
        self.update_foreign_reference(
            selected_statistic, {FclFreightRateStatistic.so1_select_count.name}, None
        )
        self.update_foreign_reference(
            original_statistic, None, self.selected_rate_numerics
        )
        self.selected_rate_numerics["select_type"] = SelectTypes.SO1.value
        self.set_revenue_desk_visit_state(original_action, "selected_for_booking")
        self.update_foreign_reference(
            original_action,
            None,
            self.original_rate_numerics,
        )

    def update_shipment(self, shipment_service_id, statistic):
        ShipmentFclFreightRateStatistic.update(
            rate_id=statistic.rate_id, validity_id=statistic.validity_id
        ).where(
            ShipmentFclFreightRateStatistic.shipment_service_id == shipment_service_id
        )
