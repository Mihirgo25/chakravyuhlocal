from services.bramhastra.clickhouse.connect import get_clickhouse_client
from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)
from services.bramhastra.models.spot_search_fcl_freight_rate_statistic import (
    SpotSearchFclFreightRateStatistic,
)
from services.bramhastra.models.checkout_fcl_freight_rate_statistic import (
    CheckoutFclFreightRateStatistic,
)
from database.rails_db import get_connection
from services.bramhastra.enums import Table, ValidityAction
from peewee import Model
from services.fcl_freight_rate.models.fcl_freight_location_cluster_mapping import (
    FclFreightLocationClusterMapping,
    FclFreightLocationCluster,
)
from micro_services.client import maps
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from playhouse.shortcuts import model_to_dict


def json_encoder(data):
    return jsonable_encoder(
        data, custom_encoder={datetime: lambda dt: dt.strftime("%Y-%m-%d %H:%M:%S")}
    )


def get_clickhouse_rows_with_column_names(result):
    rows = result.result_rows
    columns = result.column_names
    data = []
    for row in rows:
        decoded_row = []
        for value in row:
            if isinstance(value, bytes):
                decoded_value = value.decode("utf-8").replace("\x00", "")
            else:
                decoded_value = value
            decoded_row.append(decoded_value)
        data.append(dict(zip(columns, decoded_row)))
    return data


class Connection:
    def __init__(self) -> None:
        self.rails_db = get_connection()
        self.clickhouse_client = get_clickhouse_client()


class FclFreightValidity(Connection):
    def __init__(self, rate_id, validity_id, schedule_type, payment_term) -> None:
        super().__init__()
        self.rate_id = None
        self.validity_id = None
        self.fcl_freight_rate_statistics_identifier = None
        self.set_identifier_details(rate_id, validity_id, schedule_type, payment_term)

    def update_row_status_to_stale_and_return_new_row(self, row) -> dict:
        row = FclFreightRateStatistic(**row)
        new_row_dict = model_to_dict(row)
        row.sign = -1
        row.save(force_insert=True)
        new_row_dict["version"] += 1
        return new_row_dict

    def get_postgres_statistics_current_row_by_identifier(self) -> Model:
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
            "table": Table.fcl_freight_rate_statistics.value,
            "identifier": self.fcl_freight_rate_statistics_identifier,
            "sign": 1,
        }
        if row := self.clickhouse_client.query(
            "SELECT * FROM brahmastra.{table:Identifier} WHERE identifier = {identifier:FixedString(256)} and sign = {sign:Int8}",
            parameters,
        ):
            if rows := get_clickhouse_rows_with_column_names(row):
                return rows[0]

    def get_clickhouse_statistics_rows_by_rate_id(self) -> dict:
        parameters = {
            "table": Table.fcl_freight_rate_statistics,
            "identifier": self.rate_id,
        }
        if row := self.clickhouse_client.command(
            "SELECT * FROM {table:Identifier} WHERE rate_id = {identifier:UUID} FINAL",
            parameters,
        ):
            return get_clickhouse_rows_with_column_names(row)

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

    def set_identifier_details(
        self, rate_id, validity_id, schedule_type, payment_term
    ) -> None:
        self.rate_id = rate_id
        self.validity_id = validity_id
        self.fcl_freight_rate_statistics_identifier = "_".join(
            [rate_id, validity_id, payment_term, schedule_type]
        )

    def get_or_create_statistics_current_row(self) -> Model:
        row = self.get_postgres_statistics_current_row_by_identifier()
        if not row:
            row_params = self.get()
            row = self.create_stats(row_params)
        return row

    def create_stats(self, create_param) -> Model:
        return FclFreightRateStatistic.create(**create_param)

    def update_stats(self, new_params=dict(), return_new_row_without_updating=True):
        old_row = self.get_postgres_statistics_current_row_by_identifier()

        if old_row:
            print('old')
            if return_new_row_without_updating:
                return old_row
            for k, v in new_params.items():
                setattr(old_row, k, v)
                old_row.save()
        else:
            print('new')
            old_row = self.get_clickhouse_statistics_current_row_by_identifier()
            if not old_row:
                return
            row = self.update_row_status_to_stale_and_return_new_row(old_row)
            if return_new_row_without_updating:
                return row

            if new_params:
                new_params['id'] = row['id']
                self.create_stats(new_params)


class Rate:
    def __init__(self, freight) -> None:
        self.freight = freight
        self.params = []
        # ports set are main ports
        self.origin_port_id = None
        self.destination_port_id = None
        self.origin_pricing_zone_map_id = None
        self.destination_pricing_zone_map_id = None
        self.origin_region_id = None
        self.destination_region_id = None
        self.origin_continent_id = None
        self.destination_continent_id = None
        self.set_non_existing_location_details()

    def set_new_stats(self) -> int:
        return FclFreightRateStatistic.insert_many(self.params).execute()

    def set_existing_stats(self) -> None:
        if self.params:
            fcl_freight_validity = FclFreightValidity(
                rate_id=self.params[0]["rate_id"],
                validity_id=self.params[0]["validity_id"],
                payment_term=self.params[0]["payment_term"],
                schedule_type=self.params[0]["schedule_type"],
            )
        for i, new_row in enumerate(self.params):
            # we dont want to run this in async so we just make one connection for one rate
            if i:
                fcl_freight_validity.set_identifier_details(
                    rate_id=new_row["rate_id"],
                    validity_id=new_row["validity_id"],
                    schedule_type=new_row["schedule_type"],
                    payment_term=new_row["payment_term"],
                )
            if new_row["last_action"] == ValidityAction.create.value:
                fcl_freight_validity.create_stats(new_row)
            elif new_row["last_action"] == ValidityAction.update.value:
                fcl_freight_validity.update_stats(new_row)
            elif new_row["last_action"] == ValidityAction.unchanged.value:
                continue

    def set_non_existing_location_details(self) -> None:
        self.origin_port_id = (
            self.freight.origin_port_id
            if not self.freight.origin_main_port_id
            else self.freight.origin_main_port_id
        )
        self.destination_port_id = (
            self.freight.destination_port_id
            if not self.freight.destination_main_port_id
            else self.freight.destination_main_port_id
        )

        (
            self.origin_pricing_zone_map_id,
            self.destination_pricing_zone_map_id,
        ) = self.get_pricing_map_zone_ids(self.origin_port_id, self.destination_port_id)
        origin, destination = self.get_missing_location_ids(
            self.origin_port_id, self.destination_port_id
        )

        self.origin_region_id = origin.get("region_id")
        self.destination_region_id = destination.get("region_id")
        self.origin_continent_id = origin.get("continent_id")
        self.destination_continent_id = destination.get("continent_id")

    def set_formatted_data(self) -> None:
        freight = self.freight.dict(exclude={"validities"})

        for validity in self.freight.validities:
            param = freight.copy()
            param.update(validity.dict())
            param["identifier"] = "_".join(
                [
                    param["rate_id"],
                    param["validity_id"],
                    param["payment_term"],
                    param["schedule_type"],
                ]
            )
            param["origin_pricing_zone_map_id"] = self.origin_pricing_zone_map_id
            param[
                "destination_pricing_zone_map_id"
            ] = self.destination_pricing_zone_map_id
            param["origin_region_id"] = self.origin_region_id
            param["destination_region_id"] = self.destination_region_id
            param["origin_continent_id"] = self.origin_continent_id
            param["destination_continent_id"] = self.destination_continent_id
            self.params.append(param)

    def get_pricing_map_zone_ids(self, origin_port_id, destination_port_id) -> list:
        query = (
            FclFreightLocationCluster.select(
                FclFreightLocationClusterMapping.location_id,
                FclFreightLocationCluster.map_zone_id,
            )
            .join(FclFreightLocationClusterMapping)
            .where(
                FclFreightLocationClusterMapping.location_id.in_(
                    [origin_port_id, destination_port_id]
                )
            )
        )
        map_zone_location_mapping = jsonable_encoder(
            {item["location_id"]: item["map_zone_id"] for item in query.dicts()}
        )
        return map_zone_location_mapping.get(
            origin_port_id
        ), map_zone_location_mapping.get(destination_port_id)

    def get_missing_location_ids(self, origin_port_id, destination_port_id):
        response = maps.list_locations(
            data={
                "filters": {"id": [origin_port_id, destination_port_id]},
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
            return region_id_mapping.get(origin_port_id), region_id_mapping.get(
                destination_port_id
            )
        return None, None


class SpotSearch:
    def __init__(self, params) -> None:
        self.common_param = params.dict(exclude={"rates"})
        self.spot_search_params = []
        self.rates = params.rates

    def set_format_and_existing_rate_stats(self):
        fcl_freight_validity = None
        for rate in self.rates:
            param = self.common_param.copy()
            rate_dict = rate.dict()
            param.update(rate.dict(exclude={"payment_term", "schedule_type"}))

            if fcl_freight_validity is None:
                fcl_freight_validity = FclFreightValidity(**rate_dict)
            else:
                fcl_freight_validity.set_identifier_details(**rate_dict)   
            
            new_row = fcl_freight_validity.update_stats(
                return_new_row_without_updating=True
            )
            if new_row:
                param["fcl_freight_rate_statistic_id"] = new_row["id"] if isinstance(new_row,dict) else new_row.id
                self.update_spot_search_stats(fcl_freight_validity,new_row)
                self.spot_search_params.append(param)

    def set_new_stats(self) -> int:
        return SpotSearchFclFreightRateStatistic.insert_many(
            self.spot_search_params
        ).execute()

    def set_existing_stats(self) -> None:
        pass

    def update_spot_search_stats(self,fcl_freight_validity ,row):
        if isinstance(row,Model):
            row.spot_search_count+=1
            row.save()
            return
        row["spot_search_count"] += 1
        fcl_freight_validity.create_stats(row)


class Checkout(FclFreightValidity):
    def __init__(self, params) -> None:
        self.common_param = params.dict(exclude={"rates"})
        self.checkout_params = []
        self.rates = params.rates

    def set_format_and_existing_rate_stats(self):
        fcl_freight_validity = None
        for rate in self.rates:
            param = self.common_param.copy()
            rate_dict = rate.dict()
            param.update(rate.dict(exclude={"payment_term", "schedule_type"}))
            self.checkout_params.append(param)

            if not fcl_freight_validity:
                fcl_freight_validity = FclFreightValidity(**rate_dict)
            else:
                fcl_freight_validity.set_identifier_details(**rate_dict)

            new_row = fcl_freight_validity.get_current_statistic_row_by_identifier()
            self.update_checkout_params(new_row)
            fcl_freight_validity.update_stats(new_row)

    def set_new_stats(self) -> int:
        return CheckoutFclFreightRateStatistic.insert_many(
            self.checkout_params
        ).execute()

    def set_existing_stats(self) -> None:
        pass

    def update_checkout_params(self, param) -> None:
        param["checkout_count"] += 1


class Quotations(FclFreightValidity):
    def apply_create_stats(params):
        pass

    def apply_update_stats(params):
        pass


class Shipment(FclFreightValidity):
    def apply_create_stats(params):
        pass

    def apply_update_stats(params):
        pass


class Feedback(FclFreightValidity):
    pass
