from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)
from services.bramhastra.models.spot_search_fcl_freight_rate_statistic import (
    SpotSearchFclFreightRateStatistic,
)
from services.bramhastra.models.checkout_fcl_freight_rate_statistic import (
    CheckoutFclFreightRateStatistic,
)
from services.bramhastra.models.feedback_fcl_freight_rate_statistic import (
    FeedbackFclFreightRateStatistic,
)
from database.rails_db import get_connection
from services.bramhastra.enums import ValidityAction
from peewee import Model
from services.fcl_freight_rate.models.fcl_freight_location_cluster_mapping import (
    FclFreightLocationClusterMapping,
    FclFreightLocationCluster,
)
from micro_services.client import maps, common
from fastapi.encoders import jsonable_encoder
from playhouse.shortcuts import model_to_dict
from services.bramhastra.client import (
    ClickHouse,
)
from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)
from services.fcl_freight_rate.models.fcl_freight_rate_feedback import (
    FclFreightRateFeedback,
)
from services.bramhastra.enums import FeedbackAction
from services.bramhastra.models.fcl_freight_rate_request_statistics import (
    FclFreightRateRequestStatistic,
)
from services.bramhastra.enums import ShipmentAction
from services.bramhastra.models.shipment_fcl_freight_rate_statistic import (
    ShipmentFclFreightRateStatistic,
)
from database.rails_db import get_connection
from services.bramhastra.enums import ShipmentServices
from peewee import ModelSelect
from services.bramhastra.constants import FCL_MODE_MAPPINGS
from services.bramhastra.enums import FclParentMode, FclModes


STANDARD_CURRENCY = "USD"

SHIPMENT_RATE_STATS_KEYS = [
    "rate_deviation_from_latest_booking",
    "average_booking_rate",
    "rate_deviation_from_booking_rate",
    "accuracy",
]

RATE_DETAIL_KEYS = [
    "id",
    "rate_id",
    "validity_id",
    "booking_rate_count",
    "standard_price",
]


class Connection:
    def __init__(self) -> None:
        self.rails_db = get_connection()
        self.clickhouse_client = ClickHouse()


class FclFreightValidity(Connection):
    def __init__(self, rate_id, validity_id) -> None:
        super().__init__()
        self.rate_id = None
        self.validity_id = None
        self.fcl_freight_rate_statistics_identifier = None
        self.set_identifier_details(rate_id, validity_id)

    def update_row_status_to_stale_and_return_new_row(self, row) -> dict:
        row = FclFreightRateStatistic(**row)
        new_row_dict = model_to_dict(row)
        row.sign = -1
        row.save(force_insert=True)
        new_row_dict["version"] += 1
        return new_row_dict

    def get_postgres_statistics_current_row_by_identifier(self):
        return (
            FclFreightRateStatistic.select()
            .where(
                FclFreightRateStatistic.identifier
                == self.fcl_freight_rate_statistics_identifier,
                FclFreightRateStatistic.sign == 1,
            )
            .first()
        )

    def get_current_statistic_row_by_identifier(self):
        current_row = self.get_postgres_statistics_current_row_by_identifier()
        if current_row:
            return current_row.get()
        return self.get_clickhouse_statistics_current_row_by_identifier()

    def get_clickhouse_statistics_current_row_by_identifier(self) -> dict:
        parameters = {
            "identifier": self.fcl_freight_rate_statistics_identifier,
            "sign": 1,
        }
        if row := self.clickhouse_client.execute(
            f"SELECT * FROM brahmastra.{FclFreightRateStatistic._meta.table_name} WHERE identifier = %(identifier)s and sign = %(sign)s",
            parameters,
        ):
            return row[0]

    def get_clickhouse_statistics_rows_by_rate_id(self) -> dict:
        parameters = {
            "identifier": self.rate_id,
        }
        if row := self.clickhouse_client.execute(
            f"SELECT * FROM brahmastra.{FclFreightRateStatistic._meta.table_name} WHERE rate_id = %(identifier)s",
            parameters,
        ):
            return row[0]

    def get_postgres_statistics_rows_by_rate_id(self, sign=1, version=None) -> Model:
        fcl_freight_rate_statistic_query = FclFreightRateStatistic.select().where(
            FclFreightRateStatistic.rate_id == self.rate_id,
            FclFreightRateStatistic.sign == sign,
        )
        if version:
            fcl_freight_rate_statistic_query.where(
                FclFreightRateStatistic.version == version
            )

        return fcl_freight_rate_statistic_query

    def set_identifier_details(self, rate_id, validity_id) -> None:
        self.rate_id = rate_id
        self.validity_id = validity_id
        self.fcl_freight_rate_statistics_identifier = "".join(
            [rate_id, validity_id]
        ).replace("-", "")

    def get_or_create_statistics_current_row(self) -> Model:
        row = self.get_postgres_statistics_current_row_by_identifier()
        if not row:
            row_params = self.get()
            row = self.create_stats(row_params)
        return row

    def create_stats(self, create_param) -> Model:
        return FclFreightRateStatistic.create(**create_param)

    def update_stats(
        self,
        new_params=dict(),
        return_new_row_without_updating=True,
        increment_keys=None,
    ):
        old_row = self.get_postgres_statistics_current_row_by_identifier()

        if old_row:
            if return_new_row_without_updating:
                return old_row
            for k, v in new_params.items():
                setattr(old_row, k, v)
                old_row.save()
            if increment_keys is not None:
                for k in increment_keys:
                    setattr(old_row, k, getattr(old_row, k) + 1)

        else:
            old_row = self.get_clickhouse_statistics_current_row_by_identifier()
            if not old_row:
                return
            row = self.update_row_status_to_stale_and_return_new_row(old_row)
            if return_new_row_without_updating:
                return row

            if new_params:
                new_params["id"] = row["id"]
                new_params["version"] = row["version"]
                self.create_stats(new_params)

    def update(self, new_row):
        EXCLUDE_ITEMS = {
            "origin_port_id",
            "origin_country_id",
            "origin_trade_id",
            "origin_continent_id",
            "destination_port_id",
            "destination_country_id",
            "destination_trade_id",
            "destination_continent_id",
            "origin_region_id",
            "destination_region_id",
            "shipping_line_id",
            "service_provider_id",
            "importer_exporter_id",
            "container_size",
            "container_type",
            "commodity",
            "origin_main_port_id",
            "destination_main_port_id",
            "procured_by_id",
            "rate_id",
            "validity_id",
            "identifier",
        }

        select = {k: v for k, v in new_row.items() if k not in EXCLUDE_ITEMS and v}

        queries = [
            f"ALTER TABLE brahmastra.{FclFreightRateStatistic._meta.table_name} UPDATE"
        ]

        values = []
        for key in select.keys():
            values.append(f"{key} = %({key})s")

        queries.append(",".join(values))

        select["rate_id"] = new_row["rate_id"]

        queries.append(
            f"WHERE (rate_id,version) IN (SELECT rate_id, MAX(version) AS max_version FROM brahmastra.{FclFreightRateStatistic._meta.table_name} WHERE rate_id = '{select['rate_id']}' GROUP BY rate_id)"
        )

        if row := self.clickhouse_client.execute(" ".join(queries), select):
            return row[0]


class Rate:
    def __init__(self, freight) -> None:
        self.freight = freight
        self.params = []
        # ports set are main ports
        self.origin_port_id = None
        self.destination_port_id = None
        self.origin_pricing_zone_map_id = None
        self.destination_pricing_zone_map_id = None
        self.origin_main_port_id = None
        self.destination_main_port_id = None
        self.increment_keys = {}

    def set_new_stats(self) -> int:
        return FclFreightRateStatistic.insert_many(self.params).execute()

    def set_existing_stats(self) -> None:
        if self.params:
            fcl_freight_validity = FclFreightValidity(
                rate_id=self.params[0]["rate_id"],
                validity_id=self.params[0]["validity_id"],
            )
        for i, new_row in enumerate(self.params):
            if i:
                fcl_freight_validity.set_identifier_details(
                    rate_id=new_row["rate_id"],
                    validity_id=new_row["validity_id"],
                )
            if new_row["last_action"] == ValidityAction.create.value:
                for j in self.increment_keys:
                    new_row[j] = 1
                fcl_freight_validity.create_stats(new_row)
            elif new_row["last_action"] == ValidityAction.update.value:
                fcl_freight_validity.update_stats(new_row, False, self.increment_keys)
            elif new_row["last_action"] == ValidityAction.unchanged.value:
                if self.increment_keys:
                    fcl_freight_validity.update_stats(
                        new_row, False, self.increment_keys
                    )

    def set_non_existing_location_details(self) -> None:
        self.origin_port_id = self.freight.origin_port_id
        if self.freight.origin_main_port_id:
            self.origin_main_port_id = self.freight.origin_main_port_id

        self.destination_port_id = self.freight.destination_port_id
        if self.freight.destination_main_port_id:
            self.destination_main_port_id = self.freight.destination_main_port_id

        self.set_pricing_map_zone_ids()

    def get_feedback_details(self):
        if row := (
            FclFreightRateFeedback.select(
                FclFreightRateFeedback.fcl_freight_rate_id.alias("parent_rate_id"),
                FclFreightRateFeedback.validity_id.alias("parent_validity_id"),
            )
            .where(FclFreightRateFeedback.id == self.freight.source_id)
            .dicts()
        ):
            return jsonable_encoder(row.get())

        query = f"SELECT fcl_freight_rate_id AS parent_rate_id, validity_id as parent_validity_id from brahmastra.{FeedbackFclFreightRateStatistic._meta.table_name} WHERE id = '{self.freight.source_id}'"
        click = ClickHouse()
        if row := click.execute(query):
            return row[0]

    def set_formatted_data(self) -> None:
        freight = self.freight.dict(exclude={"validities", "accuracy"})

        freight["parent_mode"] = FCL_MODE_MAPPINGS.get(
            freight.get("mode") or FclModes.rms_upload.value
        )

        if (
            freight["source"] == FclModes.disliked_rate.value
            or freight.get("mode") == FclModes.disliked_rate.value
        ):
            if parent := self.get_feedback_details():
                freight.update(parent)
            self.increment_keys.add("dislikes_rate_reverted_count")

        for validity in self.freight.validities:
            param = freight.copy()
            param.update(validity.dict(exclude={"line_items"}))
            param["identifier"] = "".join(
                [
                    param["rate_id"],
                    param["validity_id"],
                ]
            ).replace("-", "")
            param["origin_pricing_zone_map_id"] = self.origin_pricing_zone_map_id
            param[
                "destination_pricing_zone_map_id"
            ] = self.destination_pricing_zone_map_id

            if param["currency"] == STANDARD_CURRENCY:
                param["standard_price"] = param["price"]
            else:
                param["standard_price"] = common.get_money_exchange_for_fcl(
                    {
                        "from_currency": param["currency"],
                        "to_currency": STANDARD_CURRENCY,
                        "price": param["price"],
                    }
                ).get("price", param["price"])

            self.params.append(param)

    def set_pricing_map_zone_ids(self) -> list:
        ids = [self.origin_port_id, self.destination_port_id]
        query = (
            FclFreightLocationCluster.select(
                FclFreightLocationClusterMapping.location_id,
                FclFreightLocationCluster.map_zone_id,
            )
            .join(FclFreightLocationClusterMapping)
            .where(FclFreightLocationClusterMapping.location_id.in_(ids))
        )
        map_zone_location_mapping = jsonable_encoder(
            {item["location_id"]: item["map_zone_id"] for item in query.dicts()}
        )

        if len(map_zone_location_mapping) < 2:
            query = FclFreightLocationCluster.select(
                FclFreightLocationCluster.base_port_id.alias("location_id"),
                FclFreightLocationCluster.map_zone_id,
            ).where(FclFreightLocationCluster.base_port_id.in_(ids))
            map_zone_location_mapping.update(
                jsonable_encoder(
                    {item["location_id"]: item["map_zone_id"] for item in query.dicts()}
                )
            )

        self.origin_pricing_zone_map_id = map_zone_location_mapping.get(
            self.origin_port_id
        )

        self.destination_pricing_zone_map_id = map_zone_location_mapping.get(
            self.destination_port_id
        )


class SpotSearch:
    def __init__(self, params) -> None:
        self.common_param = params.dict(exclude={"rates"})
        self.spot_search_id = params.spot_search_id
        self.spot_search_params = []
        self.rates = params.rates
        self.increment_keys = {"spot_search_count"}
        self.clickhouse_client = None

    def set_format_and_existing_rate_stats(self):
        fcl_freight_validity = None
        for rate in self.rates:
            param = self.common_param.copy()
            rate_dict = rate.dict(exclude={"payment_term", "schedule_type"})
            param.update(rate_dict)

            if fcl_freight_validity is None:
                fcl_freight_validity = FclFreightValidity(**rate_dict)
                self.clickhouse_client = fcl_freight_validity.clickhouse_client
            else:
                fcl_freight_validity.set_identifier_details(**rate_dict)

            new_row = fcl_freight_validity.update_stats(
                return_new_row_without_updating=True
            )
            if new_row:
                param["fcl_freight_rate_statistic_id"] = (
                    new_row["id"] if isinstance(new_row, dict) else new_row.id
                )
                self.increment_spot_search_rate_stats(fcl_freight_validity, new_row)
                self.spot_search_params.append(param)

    def set_new_stats(self) -> int:
        return SpotSearchFclFreightRateStatistic.insert_many(
            self.spot_search_params
        ).execute()

    def set_existing_stats(self) -> None:
        pass

    def increment_spot_search_rate_stats(self, fcl_freight_validity, row):
        if isinstance(row, Model):
            for key in self.increment_keys:
                setattr(row, key, getattr(row, key) + 1)
            row.save()
        else:
            for key in self.increment_keys:
                row[key] += 1
            fcl_freight_validity.create_stats(row)


class Feedback:
    def __init__(self, action, params) -> None:
        if action == FeedbackAction.create.value:
            self.params = params.dict(exclude={"likes_count", "dislikes_count"})
            self.rate_id = params.rate_id
            self.validity_id = params.validity_id
        else:
            self.params = params.dict(exclude_none=True)
        self.exclude_update_params = {"feedback_id"}

        self.feedback_id = params.feedback_id

        self.rate_stats_update_params = params.dict(
            include={
                "likes_count",
                "dislikes_count",
            }
        )
        if self.params.get("currency") != "USD":
            self.rate_stats_update_params[
                "last_indicative_rate"
            ] = common.get_money_exchange_for_fcl(
                {
                    "price": self.params.get("preferred_freight_rate"),
                    "from_currency": self.params.get("currency"),
                    "to_currency": "USD",
                }
            )[
                "price"
            ]
        else:
            self.rate_stats_update_params["last_indicative_rate"] = self.params.get(
                "preferred_freight_rate"
            )
        self.increment_keys = {}
        self.clickhouse_client = None

    def set_format_and_existing_rate_stats(self):
        fcl_freight_validity = FclFreightValidity(
            rate_id=self.rate_id, validity_id=self.validity_id
        )
        self.clickhouse_client = fcl_freight_validity.clickhouse_client
        new_row = fcl_freight_validity.update_stats(
            return_new_row_without_updating=True
        )
        if new_row:
            self.params["fcl_freight_rate_statistic_id"] = (
                new_row["id"] if isinstance(new_row, dict) else new_row.id
            )
            self.increment_feeback_rate_stats(fcl_freight_validity, new_row)

    def set_new_stats(self) -> int:
        return FeedbackFclFreightRateStatistic.insert_many(self.params).execute()

    def set_existing_stats(self) -> None:
        if (
            feedback := FeedbackFclFreightRateStatistic.select()
            .where(
                FeedbackFclFreightRateStatistic.feedback_id
                == self.params.get("feedback_id")
            )
            .first()
        ):
            for key in self.params.keys():
                if key not in self.exclude_update_params:
                    setattr(feedback, key, self.params.get(key))
            feedback.save()
            return

        if not self.clickhouse_client:
            self.clickhouse_client = ClickHouse()

        queries = [
            f"ALTER TABLE brahmastra.{FeedbackFclFreightRateStatistic._meta.table_name} UPDATE"
        ]

        values = []
        for key in self.params.keys():
            if key not in self.exclude_update_params:
                values.append(f"{key} = %({key})s")

        queries.append(",".join(values))

        queries.append(
            f"WHERE (id,version) IN (SELECT id, MAX(version) AS max_version FROM brahmastra.{FeedbackFclFreightRateStatistic._meta.table_name} WHERE feedback_id = %(feedback_id)s GROUP BY id)"
        )

        if row := self.clickhouse_client.execute(" ".join(queries), self.params):
            return row[0]

    def increment_feeback_rate_stats(self, fcl_freight_validity, row):
        if isinstance(row, Model):
            for key in self.increment_keys:
                setattr(row, key, getattr(row, key) + 1)
            for key, value in self.rate_stats_update_params.items():
                setattr(row, key, value)
            row.save()
        else:
            for key in self.increment_keys:
                row[key] += 1
            for key, value in self.rate_stats_update_params.items():
                row[key] = value
            fcl_freight_validity.create_stats(row)


class Request:
    def __init__(self, params) -> None:
        self.params = params if isinstance(params, dict) else dict(params)

        self.exclude_keys = {
            "rate_request_id",
            "origin_country_id",
            "origin_trade_id",
            "origin_continent_id",
            "destination_country_id",
            "destination_trade_id",
            "destination_continent_id",
            "origin_region_id",
            "destination_region_id",
            "container_size",
            "container_type",
            "commodity",
        }

        self.clickhouse_client = None

        self.missing_locations = dict()

        self.set_missing_locations()

    def set_missing_locations(self):
        self.set_pricing_map_zone_ids()

        self.set_missing_location_ids()

        self.params.update(self.missing_locations)

    def set_missing_location_ids(self):
        response = maps.list_locations(
            data={
                "filters": {
                    "id": [
                        self.params.get("origin_port_id"),
                        self.params.get("destination_port_id"),
                    ]
                },
                "includes": {"continent_id": True, "region_id": True, "id": True},
            }
        )
        if "list" in response and len(response["list"]) == 2:
            region_id_mapping = {
                item["id"]: dict(
                    region_id=item["region_id"], continent_id=item["continent_id"]
                )
                for item in response["list"]
            }
            origin = region_id_mapping.get(self.params.get("origin_port_id"))

            destination = region_id_mapping.get(self.params.get("destination_port_id"))

            self.missing_locations["origin_region_id"] = origin.get("region_id")
            self.missing_locations["destination_region_id"] = destination.get(
                "region_id"
            )

            self.missing_locations["origin_continent_id"] = origin.get("continent_id")
            self.missing_locations["destination_continent_id"] = destination.get(
                "continent_id"
            )

    def set_pricing_map_zone_ids(self) -> list:
        ids = [
            self.params.get("origin_port_id"),
            self.params.get("destination_port_id"),
        ]
        query = (
            FclFreightLocationCluster.select(
                FclFreightLocationClusterMapping.location_id,
                FclFreightLocationCluster.map_zone_id,
            )
            .join(FclFreightLocationClusterMapping)
            .where(FclFreightLocationClusterMapping.location_id.in_(ids))
        )
        map_zone_location_mapping = jsonable_encoder(
            {item["location_id"]: item["map_zone_id"] for item in query.dicts()}
        )

        if len(map_zone_location_mapping) < 2:
            query = FclFreightLocationCluster.select(
                FclFreightLocationCluster.base_port_id.alias("location_id"),
                FclFreightLocationCluster.map_zone_id,
            ).where(FclFreightLocationCluster.base_port_id.in_(ids))
            map_zone_location_mapping.update(
                jsonable_encoder(
                    {item["location_id"]: item["map_zone_id"] for item in query.dicts()}
                )
            )
        self.missing_locations[
            "origin_pricing_zone_map_id"
        ] = map_zone_location_mapping.get(self.params.get("origin_port_id"))

        self.missing_locations[
            "destination_pricing_zone_map_id"
        ] = map_zone_location_mapping.get(self.params.get("destination_port_id"))

    def set_new_stats(self) -> int:
        return FclFreightRateRequestStatistic(**self.params).save()

    def set_existing_stats(self) -> None:
        if (
            request := FclFreightRateRequestStatistic.select()
            .where(
                FclFreightRateRequestStatistic.rate_request_id
                == self.params.get("rate_request_id")
            )
            .first()
        ):
            for k, v in self.params:
                if k not in self.exclude_keys:
                    setattr(request, k, v)
            request.save()
            return

        if not self.clickhouse_client:
            self.clickhouse_client = ClickHouse()

        queries = [
            f"ALTER TABLE brahmastra.{FclFreightRateRequestStatistic._meta.table_name} UPDATE"
        ]

        values = []
        for key, value in self.params.items():
            if key not in self.exclude_keys and value:
                values.append(f"{key} = %({key})s")

        queries.append(",".join(values))

        queries.append(
            f"WHERE (id,version) IN (SELECT id, MAX(version) AS max_version FROM brahmastra.{FclFreightRateRequestStatistic._meta.table_name} WHERE rate_request_id = %(rate_request_id)s GROUP BY id)"
        )

        if row := self.clickhouse_client.execute(" ".join(queries), self.params):
            return row[0]


class Checkout(FclFreightValidity):
    def __init__(self, params) -> None:
        self.common_params = None
        self.checkout_params = []
        self.rates = []
        self.increment_keys = {"checkout_count"}
        self.params = params

    def set_format_and_existing_rate_stats(self):
        self.common_params = self.params.dict(exclude={"checkout_fcl_freight_services"})
        for param in self.params.checkout_fcl_freight_services:
            rate = param.rate.dict(include={"rate_id", "validity_id"})
            self.rates.append(rate)
            total_buy_price = 0
            for line_item in param.rate.line_items:
                total_buy_price += line_item["total_buy_price"]
            checkout_param = self.common_params.copy()
            checkout_param.update(param.dict(exclude={"rate"}))
            checkout_param["total_buy_price"] = total_buy_price
            checkout_param["currency"] = param.rate.line_items[0]["currency"]
            checkout_param.update(rate)

            fcl_freight_validity = FclFreightValidity(**rate)
            self.clickhouse_client = fcl_freight_validity.clickhouse_client

            new_row = fcl_freight_validity.update_stats(
                return_new_row_without_updating=True
            )

            if new_row:
                checkout_param["fcl_freight_rate_statistic_id"] = (
                    new_row["id"] if isinstance(new_row, dict) else new_row.id
                )
                self.increment_checkout_rate_stats(fcl_freight_validity, new_row)
                self.checkout_params.append(checkout_param)

    def set_new_stats(self) -> int:
        return CheckoutFclFreightRateStatistic.insert_many(
            self.checkout_params
        ).execute()

    def set_existing_stats(self) -> None:
        pass

    def increment_checkout_rate_stats(self, fcl_freight_validity, row):
        if isinstance(row, Model):
            for key in self.increment_keys:
                setattr(row, key, getattr(row, key) + 1)
            row.save()
        else:
            for key in self.increment_keys:
                row[key] += 1
            fcl_freight_validity.create_stats(row)


class Quotations(FclFreightValidity):
    def __init__(self, params) -> None:
        self.params = params
        self.shipment_params = []
        self.clickhouse_client = None
        self.shipment_id = None

    def set(self):
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

            if row := self.get(shipment_param):
                self.update(row.get("id"), shipment_param)
            else:
                ShipmentFclFreightRateStatistic.create(**shipment_param)
                increment_keys.add("buy_quotations_created")

            if shipment_param.get("is_deleted"):
                continue

            statistic.set(shipment_param, increment_keys, row)

    def update(self, id, stat):
        if not self.clickhouse_client:
            self.clickhouse_client = ClickHouse()

        queries = [
            f"ALTER TABLE brahmastra.{ShipmentFclFreightRateStatistic._meta.table_name} UPDATE"
        ]

        values = []
        for key in stat.keys():
            if key not in self.exclude_update_params:
                values.append(f"{key} = %({key})s")

        queries.append(",".join(values))

        queries.append(
            f"WHERE (id,version) IN (SELECT id, MAX(version) AS max_version FROM brahmastra.{ShipmentFclFreightRateStatistic._meta.table_name} WHERE id = {id} GROUP BY id)"
        )

        if row := self.clickhouse_client.execute(" ".join(queries), stat):
            return row[0]

    def get(self, find):
        if not self.clickhouse_client:
            self.clickhouse_client = ClickHouse()

        query = f"SELECT id from brahmastra{ShipmentFclFreightRateStatistic._meta.table_name} WHERE buy_quotation_id = %(buy_quotation_id)s AND shipment_fcl_freight_service_id = %(shipment_fcl_freight_service_id)s AND shipment_id = %(shipment_id)s"
        if row := self.clickhouse_client.execute(
            query,
            {
                k: v
                for k, v in find.items()
                if k
                in {
                    "shipment_id",
                    "buy_quotation_id",
                    "shipment_fcl_freight_service_id",
                }
            },
        ):
            return row[0]


class Statistics:
    def __init__(self, shipment_id) -> None:
        self.shipment_id = shipment_id
        self.rate = dict()
        self.original_booked_rate = None
        self.clickhouse_client = ClickHouse()
        self.original_fcl_freight_rate_statistic_id = None
        self.rate_stats_hash = dict()
        self.original_rate_stats_hash = dict()
        self.set_original_rate()
        self.total_price = None

    def set(self, param, increment_keys=None, row=None):
        if row:
            if param["total_price"] == row["total_price"]:
                return

            self.total_price = common.get_money_exchange_for_fcl(
                {
                    "price": param.get("total_price"),
                    "from_currency": param.get("currency"),
                    "to_currency": "USD",
                }
            ).get("price")

            self.set_current_rate(param.get("shipment_fcl_freight_service_id"))

            if (
                self.rate["validity_id"] == self.original_booked_rate["validity_id"]
            ) and (self.rate["rate_id"] == self.original_booked_rate["validity_id"]):
                return

            self.set_stats_hash()

            fcl_freight_validity = FclFreightValidity(**self.rate)

            new_row = fcl_freight_validity.update_stats(
                return_new_row_without_updating=True
            )

            if new_row:
                self.update_stats(
                    fcl_freight_validity, new_row, self.rate_stats_hash, increment_keys
                )

            fcl_freight_validity.set_identifier_details(**self.original_booked_rate)

            new_row = fcl_freight_validity.update_stats(
                return_new_row_without_updating=True
            )
            if new_row:
                self.update_stats(
                    fcl_freight_validity,
                    new_row,
                    self.original_rate_stats_hash,
                    increment_keys,
                )

    def set_original_statistics_id(self):
        query = f"SELECT fcl_freight_rate_statistic_id,rate_id,validity_id from brahmastra.{CheckoutFclFreightRateStatistic._meta.table_name} from shipment_id = %(shipment_id)s"
        if response := self.clickhouse_client.execute(
            query, dict(shipment_id=self.shipment_id)
        ):
            self.original_fcl_freight_rate_statistic_id = response[0][
                "fcl_freight_rate_statistic_id"
            ]

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

        queries = [
            f"SELECT * FROM brahmastra.{FclFreightRateStatistic._meta.table_name}"
        ]

        queries.append(
            f"WHERE (rate_id,version) IN (SELECT rate_id, MAX(version) AS max_version FROM brahmastra.{FclFreightRateStatistic._meta.table_name} WHERE rate_id = %(rate_id)s and validity_id = %(validity_id)s GROUP BY id)"
        )

        if row := self.clickhouse_client.execute(" ".join(queries), ans):
            self.rate = row[0]

    def set_original_rate(self):
        self.set_original_statistics_id()

        queries = [
            f"SELECT * FROM brahmastra.{FclFreightRateStatistic._meta.table_name}"
        ]

        queries.append(
            f"WHERE (rate_id,version) IN (SELECT rate_id, MAX(version) AS max_version FROM brahmastra.{FclFreightRateStatistic._meta.table_name} WHERE id = %(id)s GROUP BY id)"
        )

        if row := self.clickhouse_client.execute(
            " ".join(queries), dict(id=self.original_fcl_freight_rate_statistic_id)
        ):
            self.original_booked_rate = row[0]

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
            / self.original_booked_rate.get("booking_rate_count") + 1
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

    def update_stats(self, fcl_freight_validity, row, update_object, increment_keys):
        if isinstance(row, Model):
            for key in increment_keys:
                setattr(row, key, getattr(row, key) + 1)
            for k, v in update_object.items():
                setattr(row, k, v)
            row.save()
        else:
            for key in increment_keys:
                row[key] += 1

            for k, v in update_object.items():
                row[k] = v

            fcl_freight_validity.create_stats(row)


class Shipment(FclFreightValidity):
    def __init__(self, request) -> None:
        if request.force_update_params:
            self.update_by_shipment_id(
                request.force_update_params.dict(exclude_none=True)
            )
            return
        self.params = request.params
        self.action = request.action
        self.stats = []
        self.clickhouse_client = ClickHouse()
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
        rate_id, validity_id = self.get_rate_details_from_initial_quotation(
            self.params.shipment.source_id
        ).values()

        fcl_freight_validity = FclFreightValidity(
            rate_id=rate_id, validity_id=validity_id
        )
        self.clickhouse_client = fcl_freight_validity.clickhouse_client

        new_row = fcl_freight_validity.update_stats(
            return_new_row_without_updating=True
        )

        fcl_freight_rate_statistic_id = (
            new_row["id"] if isinstance(new_row, dict) else new_row.id
        )

        shipment_services_hash = {
            i.shipment_fcl_freight_service_id: i.dict()
            for i in self.params.fcl_freight_services
        }
        for buy_quotation in self.params.buy_quotations:
            if buy_quotation.service_type != ShipmentServices.fcl_freight_service.value:
                continue

            if not buy_quotation.is_deleted:
                self.current_total_price = buy_quotation.total_price
                self.current_currency = buy_quotation.currency

            shipment_copy = shipment.copy()
            shipment_copy["rate_id"] = rate_id
            shipment_copy["validity_id"] = validity_id
            shipment_copy.update(
                buy_quotation.dict(exclude={"service_id", "service_type"})
            )
            shipment_copy.update(shipment_services_hash[buy_quotation.service_id])
            shipment_copy[
                "fcl_freight_rate_statistic_id"
            ] = fcl_freight_rate_statistic_id
            self.stats.append(shipment_copy)

        if self.action == ShipmentAction.create.value:
            ShipmentFclFreightRateStatistic.insert_many(self.stats).execute()
            if self.params.shipment.state in self.state_increment_keys:
                if isinstance(new_row, dict):
                    new_row[self.key] += 1
                else:
                    setattr(new_row, self.key, getattr(new_row, self.key) + 1)
        elif self.action == ShipmentAction.update.value:
            self.create_or_update(new_row)

        rate_update_hash = dict()

        rate_update_hash["accuracy"] = 100

        rate_update_hash["rate_deviation_from_latest_booking"] = 0

        booking_rate_count = (
            (new_row["booking_rate_count"])
            if isinstance(new_row, dict)
            else new_row.booking_rate_count
        )

        average_booking_rate = (
            new_row["average_booking_rate"]
            if isinstance(new_row, dict)
            else new_row.average_booking_rate
        )

        standard_price = (
            new_row["standard_price"]
            if isinstance(new_row, dict)
            else new_row.standard_price
            if self.action == ShipmentAction.create.value
            else common.get_money_exchange_for_fcl(
                self.current_total_price, self.current_currency, "USD"
            )
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
            / booking_rate_count
        ) ** 0.5

        if new_row:
            for stat in self.stats:
                stat["fcl_freight_rate_statistic_id"] = (
                    new_row["id"] if isinstance(new_row, dict) else new_row.id
                )
            self.increment_shipment_rate_stats(
                fcl_freight_validity, new_row, rate_update_hash
            )

    def create_or_update(self, new_row):
        if not self.clickhouse_client:
            self.clickhouse_client = ClickHouse()
        first_row = False
        for stat in self.stats:
            if row := self.get_row(stat):
                if not first_row:
                    if self.stats[0]["state"] != row["state"]:
                        if isinstance(new_row, dict):
                            new_row[self.key] += 1
                        else:
                            setattr(new_row, self.key, getattr(new_row, self.key) + 1)
                        first_row = True
                self.update(row.get("id"), stat)
            else:
                ShipmentFclFreightRateStatistic.create(**stat)

    def get_rate_details_from_statistics_id(self, id, clickhouse_client):
        if rate := FclFreightRateStatistic.select(
            FclFreightRateStatistic.rate_id, FclFreightRateStatistic.validity_id
        ).where(FclFreightRateStatistic.id == id, FclFreightRateStatistic.sign == 1):
            return jsonable_encoder(rate.dicts().get())

        queries = [
            f"SELECT rate_id,validity_id FROM brahmastra.{FclFreightRateStatistic._meta.table_name}"
        ]

        queries.append(
            f"WHERE (id,version) IN (SELECT id, MAX(version) AS max_version FROM brahmastra.{FclFreightRateStatistic._meta.table_name} WHERE id = %(id)s GROUP BY id)"
        )

        if row := clickhouse_client.execute(" ".join(queries), dict(id=id)):
            return row[0]

    def update_by_shipment_id(self, update_params):
        clickhouse_client = ClickHouse()
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
            query = f"SELECT fcl_freight_rate_statistic_id FROM brahmastra.{ShipmentFclFreightRateStatistic._meta.table_name} WHERE shipment_id = %(shipment_id)s"

            shipment_fcl_freight_rate_statistics = clickhouse_client.execute(
                query, dict(shipment_id=update_params.get("shipment_id"))
            )

        old_state = (
            shipment_fcl_freight_rate_statistics.first().state
            if isinstance(shipment_fcl_freight_rate_statistics, ModelSelect)
            else shipment_fcl_freight_rate_statistics[0]["state"]
        )
        new_state = update_params.get("state")

        rate = self.get_rate_details_from_statistics_id(
            shipment_fcl_freight_rate_statistics.first().fcl_freight_rate_statistic_id
            if isinstance(shipment_fcl_freight_rate_statistics, ModelSelect)
            else shipment_fcl_freight_rate_statistics.get(
                "fcl_freight_rate_statistic_id"
            ),
            clickhouse_client,
        )

        fcl_freight_validity = FclFreightValidity(**rate)

        new_row = fcl_freight_validity.update_stats(
            return_new_row_without_updating=True
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
                getattr(new_row, new_key)
                if isinstance(new_row, Model)
                else new_row[new_key]
            ) + 1
            rate_update_params[old_key] = (
                getattr(new_row, old_key)
                if isinstance(new_row, Model)
                else new_row[old_key]
            ) - 1

        self.increment_shipment_rate_stats(
            fcl_freight_validity, new_row, rate_update_params, apply_increment=False
        )

        if isinstance(shipment_fcl_freight_rate_statistics, ModelSelect):
            for (
                shipment_fcl_freight_rate_statistic
            ) in shipment_fcl_freight_rate_statistics:
                for k, v in update_params.items():
                    if k in avoid_keys:
                        continue
                    setattr(shipment_fcl_freight_rate_statistic, k, v)
                shipment_fcl_freight_rate_statistic.save()
            return

        queries = [
            f"ALTER TABLE brahmastra.{ShipmentFclFreightRateStatistic._meta.table_name} UPDATE"
        ]

        values = []
        for key in update_params.keys():
            if key not in avoid_keys:
                values.append(f"{key} = %({key})s")

        queries.append(",".join(values))

        queries.append(
            f"WHERE (id,version) IN (SELECT id, MAX(version) AS max_version FROM brahmastra.{ShipmentFclFreightRateStatistic._meta.table_name} WHERE shipment_id = %(shipment_id)s GROUP BY id)"
        )

        if row := clickhouse_client.execute(" ".join(queries), update_params):
            return row[0]

    def update(self, id, stat):
        if not self.clickhouse_client:
            self.clickhouse_client = ClickHouse()

        if (
            shipment := ShipmentFclFreightRateStatistic.select()
            .where(ShipmentFclFreightRateStatistic.id == id)
            .first()
        ):
            for k, v in stat.items():
                setattr(shipment, k, v)
            shipment.save()
            return

        queries = [
            f"ALTER TABLE brahmastra.{ShipmentFclFreightRateStatistic._meta.table_name} UPDATE"
        ]

        values = []
        for key in stat.keys():
            if key not in self.exclude_update_params:
                values.append(f"{key} = %({key})s")

        queries.append(",".join(values))

        queries.append(
            f"WHERE (id,version) IN (SELECT id, MAX(version) AS max_version FROM brahmastra.{ShipmentFclFreightRateStatistic._meta.table_name} WHERE id = {id} GROUP BY id)"
        )

        if row := self.clickhouse_client.execute(" ".join(queries), stat):
            return row[0]

    def get_row(self, stat):
        filt = {
            k: v
            for k, v in stat.items()
            if k
            in {
                "shipment_id",
                "buy_quotation_id",
                "shipment_fcl_freight_service_id",
            }
        }
        if (
            shipment := ShipmentFclFreightRateStatistic.select(
                ShipmentFclFreightRateStatistic.id
            )
            .filter(filt)
            .first()
        ):
            return list(shipment.dicts())[0]
        query = f"SELECT id from brahmastra.{ShipmentFclFreightRateStatistic._meta.table_name} WHERE buy_quotation_id = %(buy_quotation_id)s AND shipment_fcl_freight_service_id = %(shipment_fcl_freight_service_id)s AND shipment_id = %(shipment_id)s"
        if row := self.clickhouse_client.execute(
            query,
            filt,
        ):
            return row[0]

    def increment_shipment_rate_stats(
        self, fcl_freight_validity, row, update_object, apply_increment=True
    ):
        if isinstance(row, Model):
            if apply_increment:
                for key in self.increment_keys:
                    setattr(row, key, getattr(row, key) + 1)
            for k, v in update_object.items():
                setattr(row, k, v)
            row.save()
        else:
            if apply_increment:
                for key in self.increment_keys:
                    row[key] += 1

            for k, v in update_object.items():
                row[k] = v

            fcl_freight_validity.create_stats(row)

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
        query = f"SELECT rate_id,validity_id FROM brahmastra.{CheckoutFclFreightRateStatistic._meta.table_name} WHERE checkout_id = %(source_id)s"
        if response := self.clickhouse_client.execute(query, dict(source_id=source_id)):
            return response[0]


class RevenueDesk(FclFreightValidity):
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
        fcl_freight_validity = None

        for validity_id in request.validities:
            if not fcl_freight_validity:
                fcl_freight_validity = FclFreightValidity(request.rate_id, validity_id)
            else:
                fcl_freight_validity.set_identifier_details(
                    request.rate_id, validity_id
                )

            new_row = fcl_freight_validity.update_stats(
                return_new_row_without_updating=True
            )

            self.increment_keys = {"revenue_desk_visit_count"}

            if new_row:
                self.increment_rd_rate_stats(fcl_freight_validity, new_row)
        return

    def update_selected_for_preference_count(self, request):
        fcl_freight_validity = FclFreightValidity(
            request.selected_for_preference.rate_id,
            request.selected_for_preference.validity_id,
        )

        new_row = fcl_freight_validity.update_stats(
            return_new_row_without_updating=True
        )

        self.increment_keys = {"so1_visit_count"}

        total_priority = (
            new_row.total_priority
            if isinstance(new_row, Model)
            else new_row.get("total_priority")
        )

        total_priority += request.selected_for_preference.given_priority

        update_params = dict(total_priority=total_priority)

        if new_row:
            self.increment_rd_rate_stats(fcl_freight_validity, new_row, update_params)

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

        query = f"SELECT fcl_freight_rate_statistic_id FROM brahmastra.{ShipmentFclFreightRateStatistic._meta.table_name} WHERE shipment_fcl_freight_service_id = %(shipment_fcl_freight_service_id)s"

        if row := self.clickhouse_client.execute(
            query,
            dict(shipment_fcl_freight_service_id=self.shipment_fcl_freight_service_id),
        ):
            self.original_fcl_freight_rate_statistic_id = row[0][
                "fcl_freight_rate_statistic_id"
            ]

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
        queries = [
            f"SELECT {','.join(SHIPMENT_RATE_STATS_KEYS + RATE_DETAIL_KEYS)} FROM brahmastra.{FclFreightRateStatistic._meta.table_name}"
        ]

        queries.append(
            f"WHERE (id,version) IN (SELECT id, MAX(version) AS max_version FROM brahmastra.{FclFreightRateStatistic._meta.table_name} WHERE id = %(id)s GROUP BY id)"
        )

        if row := self.clickhouse_client.execute(
            " ".join(queries), dict(id=self.original_fcl_freight_rate_statistic_id)
        ):
            self.original_booked_rate = row[0]

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
                or 1
            )
            + self.rate.get("standard_price")
        ) / (self.original_booked_rate.get("booking_rate_count") + 1)
        self.rate_stats_hash[key] = (
            (
                self.rate.get("average_booking_rate")
                * self.rate.get("booking_rate_count")
                or 1
            )
            + self.rate.get("standard_price")
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
        self.rate_stats_hash[key] = 0

    def set_accuracy(self, key):
        self.rate_stats_hash[key] = (
            1
            - (
                abs(
                    self.rate_stats_hash.get("average_booking_rate")
                    - self.rate.get("standard_price")
                )
                / self.rate_stats_hash.get("average_booking_rate")
            )
        ) * 100
        self.original_rate_stats_hash[key] = (
            (
                1
                - abs(
                    self.original_booked_rate.get("standard_price")
                    - self.rate.get("standard_price")
                )
                / self.original_booked_rate.get("standard_price")
            )
            * 100
            if self.original_booked_rate.get("standard_price") != 0
            else 100
        )

    def set_rate_stats(self):
        fcl_freight_validity = FclFreightValidity(**self.rate)
        new_row = fcl_freight_validity.update_stats(
            return_new_row_without_updating=True
        )
        self.rate = (
            jsonable_encoder(model_to_dict(new_row))
            if isinstance(new_row, Model)
            else new_row.copy()
        )

        self.rate = {
            key: self.rate[key]
            for key in SHIPMENT_RATE_STATS_KEYS + RATE_DETAIL_KEYS
            if key in self.rate
        }

        if new_row:
            self.increment_rd_rate_stats(
                fcl_freight_validity, new_row, self.rate_stats_hash
            )

        self.clickhouse_client = fcl_freight_validity.clickhouse_client
        self.set_original_rate()
        if (
            self.original_booked_rate["rate_id"] == self.original_booked_rate["rate_id"]
        ) and (self.original_booked_rate["validity_id"] == self.rate["validity_id"]):
            return
        self.set_stats_hash()

        fcl_freight_validity.set_identifier_details(
            self.original_booked_rate.get("rate_id"),
            self.original_booked_rate.get("validity_id"),
        )

        new_row = fcl_freight_validity.update_stats(
            return_new_row_without_updating=True
        )
        if new_row:
            self.increment_rd_rate_stats(
                fcl_freight_validity, new_row, self.original_rate_stats_hash
            )

    def increment_rd_rate_stats(self, fcl_freight_validity, row, update_object={}):
        if isinstance(row, Model):
            for key in self.increment_keys:
                setattr(row, key, getattr(row, key) + 1)
            for k, v in update_object.items():
                setattr(row, k, v)
            row.save()
        else:
            for key in self.increment_keys:
                row[key] += 1

            for k, v in update_object.items():
                row[k] = v

            fcl_freight_validity.create_stats(row)
