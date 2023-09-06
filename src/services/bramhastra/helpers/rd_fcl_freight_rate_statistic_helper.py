from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)
from fastapi.encoders import jsonable_encoder
from playhouse.shortcuts import model_to_dict
from services.bramhastra.models.shipment_fcl_freight_rate_statistic import (
    ShipmentFclFreightRateStatistic,
)
from services.bramhastra.helpers.common_statistic_helper import get_identifier
from services.bramhastra.constants import SHIPMENT_RATE_STATS_KEYS, RATE_DETAIL_KEYS


class RevenueDesk:
    def __init__(self, params) -> None:
        if not getattr(params, "selected_for_booking"):
            return

        self.rate = dict()
        self.original_booked_rate = None
        self.shipment_id = params.shipment_id
        self.shipment_fcl_freight_service_id = params.shipment_fcl_freight_service_id
        self.increment_keys = {
            "so1_select_count",
            "booking_rate_count",
        }
        self.clickhouse_client = None
        self.original_fcl_freight_rate_statistic_id = None
        self.rate_stats_hash = dict()
        self.original_rate_stats_hash = dict()
        self.set_current_rate(params)

    def update_rd_visit_count(self, request):
        for validity_id in request.validities:
            fcl_freight_rate_statistic = (
                FclFreightRateStatistic.select()
                .where(
                    FclFreightRateStatistic.identifier
                    == get_identifier(request.rate_id, validity_id)
                )
                .first()
            )

            self.increment_keys = {"revenue_desk_visit_count"}

            fcl_freight_rate_statistic.updated_at = request.created_at

            if fcl_freight_rate_statistic:
                self.increment_rd_rate_stats(fcl_freight_rate_statistic)

    def update_selected_for_preference_count(self, request):
        fcl_freight_rate_statistic = (
            FclFreightRateStatistic.select()
            .where(
                FclFreightRateStatistic.identifier
                == get_identifier(
                    request.selected_for_preference.rate_id,
                    request.selected_for_preference.validity_id,
                )
            )
            .first()
        )
        
        if fcl_freight_rate_statistic:

            fcl_freight_rate_statistic.updated_at = request.created_at

            self.increment_keys = {"so1_visit_count"}

            total_priority = (fcl_freight_rate_statistic.total_priority or 1) + (
                request.selected_for_preference.given_priority or 1
            )

            update_params = dict(total_priority=total_priority)

            self.increment_rd_rate_stats(fcl_freight_rate_statistic, update_params)

    def set_current_rate(self, params):
        if getattr(params, "selected_for_booking"):
            self.rate["rate_id"] = params.selected_for_booking.rate_id
            self.rate["validity_id"] = params.selected_for_booking.validity_id

    def set_original_statistics_id(self):
        if (
            shipment := ShipmentFclFreightRateStatistic.select(
                ShipmentFclFreightRateStatistic.fcl_freight_rate_statistic_id
            )
            .where(
                ShipmentFclFreightRateStatistic.shipment_fcl_freight_service_id
                == self.shipment_fcl_freight_service_id,
                ShipmentFclFreightRateStatistic.sign == 1,
            )
            .first()
        ):
            self.original_fcl_freight_rate_statistic_id = (
                shipment.fcl_freight_rate_statistic_id
            )

        shipment_fcl_freight_rate_statistic = (
            ShipmentFclFreightRateStatistic.select(
                ShipmentFclFreightRateStatistic.fcl_freight_rate_statistic_id
            )
            .where(
                ShipmentFclFreightRateStatistic.shipment_fcl_freight_service_id
                == self.shipment_fcl_freight_service_id
            )
            .first()
        )

        self.original_fcl_freight_rate_statistic_id = (
            shipment_fcl_freight_rate_statistic.fcl_freight_rate_statistic_id
        )

    def set_original_rate(self):
        self.set_original_statistics_id()

        if fcl := FclFreightRateStatistic.select(
            FclFreightRateStatistic.id,
            FclFreightRateStatistic.rate_id,
            FclFreightRateStatistic.validity_id,
            FclFreightRateStatistic.booking_rate_count,
            FclFreightRateStatistic.rate_deviation_from_latest_booking,
            FclFreightRateStatistic.rate_deviation_from_booking_rate,
            FclFreightRateStatistic.accuracy,
            FclFreightRateStatistic.average_booking_rate,
            FclFreightRateStatistic.standard_price,
        ).where(
            FclFreightRateStatistic.id == self.original_fcl_freight_rate_statistic_id,
            FclFreightRateStatistic.sign == 1,
        ):
            self.original_booked_rate = jsonable_encoder(fcl.dicts().get())

    def set_stats_hash(self):
        for key in SHIPMENT_RATE_STATS_KEYS:
            eval(f"self.set_{key}(key)")

    def set_rate_deviation_from_latest_booking(self, key):
        self.original_rate_stats_hash[key] = self.rate.get(
            "standard_price"
        ) - self.original_booked_rate.get("standard_price")

        self.rate_stats_hash[key] = 0

    def set_average_booking_rate(self, key):
        self.original_rate_stats_hash[key] = (
            (
                self.original_booked_rate.get("average_booking_rate")
                * self.original_booked_rate.get("booking_rate_count")
            )
            + self.rate.get("standard_price")
        ) / (self.original_booked_rate.get("booking_rate_count") + 1)
        self.rate_stats_hash[key] = (
            (
                self.rate.get("average_booking_rate")
                * self.rate.get("booking_rate_count")
            )
            + self.rate.get("standard_price")
        ) / (self.rate.get("booking_rate_count") + 1)

    def set_rate_deviation_from_booking_rate(self, key):
        self.original_rate_stats_hash[key] = self.rate.get(
            "standard_price"
        ) - self.original_booked_rate.get("standard_price")
        self.rate_stats_hash[key] = 0

    def set_accuracy(self, key):
        self.rate_stats_hash[key] = round(
            (
                1
                - (
                    abs(
                        self.rate_stats_hash.get("average_booking_rate")
                        - self.rate.get("standard_price")
                    )
                    / (self.rate_stats_hash.get("average_booking_rate") or 1)
                )
            )
            * 100,
            2,
        )
        self.original_rate_stats_hash[key] = (
            round(
                (
                    1
                    - abs(
                        self.original_booked_rate.get("standard_price")
                        - self.rate.get("standard_price")
                    )
                    / (self.original_booked_rate.get("standard_price") or 1)
                )
                * 100,
                2,
            )
            if self.original_booked_rate.get("standard_price") != 0
            else 100
        )

    def set_rate_stats(self, created_at):
        fcl_freight_rate_statistic = (
            FclFreightRateStatistic.select()
            .where(FclFreightRateStatistic.identifier == get_identifier(**self.rate))
            .first()
        )

        self.rate = jsonable_encoder(model_to_dict(fcl_freight_rate_statistic))

        self.rate = {
            key: self.rate[key]
            for key in SHIPMENT_RATE_STATS_KEYS + RATE_DETAIL_KEYS
            if key in self.rate
        }

        self.set_original_rate()
        if (self.original_booked_rate["rate_id"] == self.rate["rate_id"]) and (
            self.original_booked_rate["validity_id"] == self.rate["validity_id"]
        ):
            return
        self.set_stats_hash()

        if fcl_freight_rate_statistic:
            self.increment_rd_rate_stats(
                fcl_freight_rate_statistic, self.rate_stats_hash
            )
            fcl_freight_rate_statistic.updated_at = created_at

        fcl_freight_rate_statistic = (
            FclFreightRateStatistic.select()
            .where(
                FclFreightRateStatistic.identifier
                == get_identifier(
                    self.original_booked_rate.get("rate_id"),
                    self.original_booked_rate.get("validity_id"),
                )
            )
            .first()
        )

        if fcl_freight_rate_statistic:
            fcl_freight_rate_statistic.updated_at = created_at
            self.increment_keys.remove("so1_select_count")
            self.increment_rd_rate_stats(
                fcl_freight_rate_statistic, self.original_rate_stats_hash
            )

    def increment_rd_rate_stats(self, row, update_object={}):
        for key in self.increment_keys:
            setattr(row, key, getattr(row, key) + 1)
        for k, v in update_object.items():
            if v is not None:
                setattr(row, k, v)
        row.save()
