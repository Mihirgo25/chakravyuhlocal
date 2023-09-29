from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)
from services.bramhastra.models.checkout_fcl_freight_rate_statistic import (
    CheckoutFclFreightRateStatistic,
)
from micro_services.client import common
from fastapi.encoders import jsonable_encoder
from services.bramhastra.enums import ShipmentAction
from services.bramhastra.models.shipment_fcl_freight_rate_statistic import (
    ShipmentFclFreightRateStatistic,
)
from services.bramhastra.enums import ShipmentServices
from services.bramhastra.helpers.common_statistic_helper import get_identifier
from services.bramhastra.enums import Fcl


class Shipment:
    def __init__(self, request) -> None:
        if request.force_update_params:
            self.update_by_shipment_id(
                request.force_update_params.dict(exclude_none=True)
            )
            return
        self.params = request.params
        self.action = request.action
        self.stats = []
        self.increment_keys = {
            "bookings_created",
            "buy_quotations_created",
            "shipment_is_active_count",
        }
        self.exclude_update_params = {
            "id",
            "shipment_fcl_freight_service_id",
            "shipment_id",
        }
        self.current_total_price = None
        self.state_increment_keys = {
            "cancelled",
            "completed",
            "confirmed_by_importer_exporter",
            "aborted",
            "shipment_received",
        }
        self.key = (
            f"shipment_{self.params.shipment.state}_count"
            if self.params.shipment.state != "shipment_received"
            else "shipment_received_count"
        )

    def format(self):
        shipment = self.params.shipment.dict()
        quotation = self.get_rate_details_from_initial_quotation(
            self.params.shipment.source_id
        )
        if quotation is None:
            return

        fcl_freight_rate_statistic = (
            FclFreightRateStatistic.select()
            .where(
                FclFreightRateStatistic.identifier
                == get_identifier(
                    rate_id=quotation["rate_id"], validity_id=quotation["validity_id"]
                )
            )
            .first()
        )

        shipment_services_hash = {
            i.shipment_fcl_freight_service_id: i.dict()
            for i in self.params.fcl_freight_services
        }

        if not self.params.buy_quotations:
            return

        for buy_quotation in self.params.buy_quotations:
            if buy_quotation.service_type != ShipmentServices.fcl_freight_service.value:
                continue

            if not buy_quotation.is_deleted:
                self.current_total_price = buy_quotation.total_price
                self.current_currency = buy_quotation.currency

            shipment_copy = shipment.copy()
            shipment_copy["rate_id"] = quotation["rate_id"]
            shipment_copy["validity_id"] = quotation["validity_id"]
            shipment_copy.update(
                buy_quotation.dict(exclude={"service_id", "service_type"})
            )
            shipment_copy.update(
                shipment_services_hash.get(buy_quotation.service_id, {})
            )
            shipment_copy[
                "fcl_freight_rate_statistic_id"
            ] = fcl_freight_rate_statistic.id
            self.stats.append(shipment_copy)

        if self.action == ShipmentAction.create.value:
            ShipmentFclFreightRateStatistic.insert_many(self.stats).execute()
            if self.params.shipment.state in self.state_increment_keys:
                setattr(
                    fcl_freight_rate_statistic,
                    self.key,
                    getattr(fcl_freight_rate_statistic, self.key) + 1,
                )
                fcl_freight_rate_statistic.save()
        elif self.action == ShipmentAction.update.value:
            self.create_or_update(fcl_freight_rate_statistic)

        fcl_freight_rate_statistic.save()

        rate_update_hash = dict()

        rate_update_hash["accuracy"] = 100

        rate_update_hash["rate_deviation_from_latest_booking"] = 0

        booking_rate_count = fcl_freight_rate_statistic.booking_rate_count

        average_booking_rate = fcl_freight_rate_statistic.average_booking_rate

        standard_price = (
            fcl_freight_rate_statistic.standard_price
            if self.action == ShipmentAction.create.value
            else common.get_money_exchange_for_fcl(
                {
                    "from_currency": self.current_currency,
                    "to_currency": Fcl.default_currency.value,
                    "price": self.current_total_price,
                }
            ).get("price", self.current_total_price)
        )

        rate_update_hash["booking_rate_count"] = booking_rate_count + 1

        rate_update_hash["average_booking_rate"] = (
            ((average_booking_rate * booking_rate_count) + standard_price)
            / (booking_rate_count + 1)
            if average_booking_rate
            else standard_price
        )

        rate_update_hash["rate_deviation_from_booking_rate"] = (
            (standard_price - rate_update_hash.get("average_booking_rate")) ** 2
            / (booking_rate_count or 1)
        ) ** 0.5

        if fcl_freight_rate_statistic:
            for stat in self.stats:
                stat["fcl_freight_rate_statistic_id"] = fcl_freight_rate_statistic.id
            self.increment_shipment_rate_stats(
                fcl_freight_rate_statistic, rate_update_hash
            )

    def create_or_update(self, new_row):
        first_row = False
        for stat in self.stats:
            if (
                shipment := ShipmentFclFreightRateStatistic.select()
                .where(
                    ShipmentFclFreightRateStatistic.shipment_id
                    == stat.get("shipment_id"),
                    ShipmentFclFreightRateStatistic.buy_quotation_id
                    == stat.get("buy_quotation_id"),
                    ShipmentFclFreightRateStatistic.shipment_fcl_freight_service_id
                    == stat.get("shipment_fcl_freight_service_id"),
                )
                .first()
            ):
                if not first_row:
                    if self.stats[0]["state"] != shipment.state:
                        setattr(new_row, self.key, getattr(new_row, self.key) + 1)
                        new_row.save()
                        first_row = True
                for k, v in stat.items():
                    if v:
                        setattr(shipment, k, v)
                shipment.save()
            else:
                ShipmentFclFreightRateStatistic.create(**stat)

    def get_rate_details_from_statistics_id(self, id):
        if rate := FclFreightRateStatistic.select(
            FclFreightRateStatistic.rate_id, FclFreightRateStatistic.validity_id
        ).where(FclFreightRateStatistic.id == id, FclFreightRateStatistic.sign == 1):
            return jsonable_encoder(rate.dicts().get())

    def update_by_shipment_id(self, update_params):
        rate_update_params = dict()
        avoid_keys = {"shipment_id"}
        shipment_fcl_freight_rate_statistics = (
            ShipmentFclFreightRateStatistic.select().where(
                ShipmentFclFreightRateStatistic.shipment_id
                == update_params.get("shipment_id"),
                ShipmentFclFreightRateStatistic.sign == 1,
            )
        )

        if not shipment_fcl_freight_rate_statistics:
            return
        old_state = shipment_fcl_freight_rate_statistics.first().state
        new_state = update_params.get("state")

        fcl_freight_rate_statistic = (
            FclFreightRateStatistic.select()
            .where(
                FclFreightRateStatistic.id
                == shipment_fcl_freight_rate_statistics.first().fcl_freight_rate_statistic_id
            )
            .first()
        )

        rate_update_params = {}

        if old_state != new_state:
            old_key = (
                f"shipment_{old_state}_count"
                if old_state != "shipment_received"
                else "shipment_received_count"
            )
            new_key = (
                f"shipment_{new_state}_count"
                if new_state != "shipment_received"
                else "shipment_received_count"
            )
            rate_update_params[new_key] = (
                getattr(fcl_freight_rate_statistic, new_key) + 1
            )
            rate_update_params[old_key] = (
                getattr(fcl_freight_rate_statistic, old_key) - 1
            )

        self.increment_shipment_rate_stats(
            fcl_freight_rate_statistic, rate_update_params, apply_increment=False
        )

        for shipment_fcl_freight_rate_statistic in shipment_fcl_freight_rate_statistics:
            for k, v in update_params.items():
                if k in avoid_keys and not v:
                    continue
                setattr(shipment_fcl_freight_rate_statistic, k, v)
            shipment_fcl_freight_rate_statistic.save()

    def increment_shipment_rate_stats(self, row, update_object, apply_increment=True):
        if apply_increment:
            for key in self.increment_keys:
                setattr(row, key, getattr(row, key) + 1)
        for k, v in update_object.items():
            if v:
                setattr(row, k, v)
        row.save()

    def get_rate_details_from_initial_quotation(self, source_id):
        if (
            response := CheckoutFclFreightRateStatistic.select(
                CheckoutFclFreightRateStatistic.rate_id,
                CheckoutFclFreightRateStatistic.validity_id,
            )
            .where(CheckoutFclFreightRateStatistic.checkout_id == source_id)
            .dicts()
        ):
            return jsonable_encoder(response.get())
