from services.bramhastra.models.air_freight_rate_statistic import (
    AirFreightRateStatistic,
)
from services.bramhastra.models.checkout_air_freight_rate_statistic import (
    CheckoutAirFreightRateStatistic,
)
from database.rails_db import get_connection
from micro_services.client import common
from services.bramhastra.models.air_freight_rate_statistic import (
    AirFreightRateStatistic,
)
from services.bramhastra.models.shipment_air_freight_rate_statistics import (
    ShipmentAirFreightRateStatistic,
)
from database.rails_db import get_connection
from services.bramhastra.constants import SHIPMENT_RATE_STATS_KEYS
from playhouse.shortcuts import model_to_dict
from services.bramhastra.helpers.common_statistic_helper import get_air_freight_identifier


class Quotations:
    def __init__(self, params) -> None:
        self.params = params
        self.shipment_params = []
        self.shipment_id = None

    def set(self) -> None:
        row = None

        if not self.params[0]:
            return

        statistic = Statistics(self.params[0].shipment.shipment_id)
        for param in self.params:
            shipment_param = dict()
            for _, object in param:
                if not object:
                    continue
                shipment_param.update(object.dict(exclude_none=True))

            if not self.shipment_id:
                self.shipment_id = shipment_param.get("shipment_id")

            increment_keys = {"booking_rate_count"}

            if row := self.update(shipment_param):
                pass
            else:
                ShipmentAirFreightRateStatistic.create(**shipment_param)
                increment_keys.add("buy_quotations_created")

            if shipment_param.get("is_deleted"):
                continue

            statistic.set(shipment_param, increment_keys, row)

    def update(self, find) -> int:
        shipment_air_freight_rate_statistic = (
            ShipmentAirFreightRateStatistic.select()
            .where(
                ShipmentAirFreightRateStatistic.shipment_id == find.get("shipment_id"),
                ShipmentAirFreightRateStatistic.buy_quotation_id
                == find.get("buy_quotation_id"),
                ShipmentAirFreightRateStatistic.shipment_air_freight_service_id
                == find.get("shipment_air_freight_service_id"),
            )
            .first()
        )

        if shipment_air_freight_rate_statistic:
            for key, value in find.items():
                if key not in self.exclude_update_params and value is not None:
                    setattr(shipment_air_freight_rate_statistic, key, value)

            shipment_air_freight_rate_statistic.save()

            return shipment_air_freight_rate_statistic.id


class Statistics:
    def __init__(self, shipment_id) -> None:
        self.shipment_id = shipment_id
        self.rate = dict()
        self.original_booked_rate = None
        self.original_air_freight_rate_statistic_id = None
        self.rate_stats_hash = dict()
        self.original_rate_stats_hash = dict()
        self.set_original_rate()
        self.total_price = None

    def set(self, param, increment_keys=None, row=None):
        if row:
            if param["total_price"] == row["total_price"]:
                return

            self.total_price = common.get_money_exchange_for_Air(
                {
                    "price": param.get("total_price"),
                    "from_currency": param.get("currency"),
                    "to_currency": "USD",
                }
            ).get("price")

            self.set_current_rate(param.get("shipment_air_freight_service_id"))

            if (
                self.rate["validity_id"] == self.original_booked_rate["validity_id"]
            ) and (self.rate["rate_id"] == self.original_booked_rate["validity_id"]):
                return

            self.set_stats_hash()

            air_freight_rate_statistic = (
                AirFreightRateStatistic.select()
                .where(
                    AirFreightRateStatistic.identifier == get_air_freight_identifier(**self.rate)
                )
                .first()
            )

            if air_freight_rate_statistic:
                self.update_stats(
                    air_freight_rate_statistic, self.rate_stats_hash, increment_keys
                )

            air_freight_rate_statistic = AirFreightRateStatistic.select().where(
                AirFreightRateStatistic.identifier
                == get_air_freight_identifier(**self.original_booked_rate)
            )

            if air_freight_rate_statistic:
                self.update_stats(
                    air_freight_rate_statistic,
                    self.original_rate_stats_hash,
                    increment_keys,
                )

    def set_original_statistics_id(self):
        if (
            checkout_air_freight_rate_statistic := CheckoutAirFreightRateStatistic.select(
                CheckoutAirFreightRateStatistic.air_freight_rate_statistic_id,
                CheckoutAirFreightRateStatistic.rate_id,
                CheckoutAirFreightRateStatistic.validity_id,
            )
            .where(CheckoutAirFreightRateStatistic.shipment_id == self.shipment_id)
            .first()
        ):
            self.original_air_freight_rate_statistic_id = (
                checkout_air_freight_rate_statistic.air_freight_rate_statistic_id
            )

    def set_current_rate(self, service_id):
        ans = None
        conn = get_connection()
        with conn:
            with conn.cursor() as cur:
                cur = conn.cursor()
                sql = f"select rate_id,selected_validity_id as validity_id from revenue_desk_show_rates where is_selected_for_booking = %s and shipment_id = %s and service_id = %s"
                result = cur.execute(sql, (True, self.shipment_id, service_id))
                columns = [col[0] for col in result.description]
                ans = dict(zip(columns, result.fetchone()))
                cur.close()
        conn.close()
        
        if ans is None:
            raise ValueError("current rate not found in revenue desk")

        air_freight_rate_statistic = (
            AirFreightRateStatistic.select()
            .where(AirFreightRateStatistic.identifier == get_air_freight_identifier(**ans))
            .first()
        )

        if air_freight_rate_statistic:
            self.rate = model_to_dict(air_freight_rate_statistic)

    def set_original_rate(self):
        self.set_original_statistics_id()

        air_freight_rate_statistic = (
            AirFreightRateStatistic.select()
            .where(
                AirFreightRateStatistic.id
                == self.original_air_freight_rate_statistic_id
            )
            .first()
        )

        if air_freight_rate_statistic:
            self.original_booked_rate = model_to_dict(air_freight_rate_statistic)

    def set_stats_hash(self):
        if not self.total_price:
            return
        for key in SHIPMENT_RATE_STATS_KEYS:
            eval(f"self.set_{key}(key)")

    def set_rate_deviation_from_latest_booking(self, key):
        self.original_rate_stats_hash[key] = abs(
            self.total_price - self.original_booked_rate("standard_price")
        )

        self.rate_stats_hash[key] = abs(self.total_price - self.rate["standard_price"])

    def set_average_booking_rate(self, key):
        self.original_rate_stats_hash[key] = (
            (
                self.original_booked_rate.get("average_booking_rate")
                * self.original_booked_rate.get("booking_rate_count")
                or 1
            )
            + self.total_price
        ) / (self.original_booked_rate.get("booking_rate_count") + 1)

        self.rate_stats_hash[key] = (
            (
                self.rate.get("average_booking_rate")
                * self.rate.get("booking_rate_count")
                or 1
            )
            + self.total_price
        ) / (self.rate.get("booking_rate_count") + 1)

    def set_rate_deviation_from_booking_rate(self, key):
        self.original_rate_stats_hash[key] = (
            (
                self.original_booked_rate.get("standard_price")
                - self.original_rate_stats_hash.get("average_booking_rate")
            )
            ** 2
            / self.original_booked_rate.get("booking_rate_count")
            + 1
        ) ** 0.5
        self.rate_stats_hash[key] = abs(
            self.rate_stats_hash["average_booking_rate"]
            - self.rate.get("standard_price")
        )

    def set_accuracy(self, key):
        self.rate_stats_hash[key] = (
            1
            - abs(self.total_price - self.rate_stats_hash.get("standard_price"))
            / self.total_price
        ) * 100
        self.original_rate_stats_hash[key] = (
            1
            - abs(self.total_price - self.original_booked_rate.get("standard_price"))
            / self.total_price
        ) * 100

    def update_stats(self, row, update_object, increment_keys):
        for key in increment_keys:
            setattr(row, key, getattr(row, key) + 1)
        for k, v in update_object.items():
            setattr(row, k, v)
        row.save()
