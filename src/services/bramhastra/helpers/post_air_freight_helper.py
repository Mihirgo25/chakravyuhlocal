from services.bramhastra.clickhouse.connect import get_clickhouse_client
from services.bramhastra.models.air_freight_rate_statistic import (
    AirFreightRateStatistic,
)
# from services.bramhastra.models.spot_search_fcl_freight_rate_statistic import SpotSearchFclFreightRateStatistic
from database.rails_db import get_connection
from services.bramhastra.enums import Table, ValidityAction
from peewee import Model
from services.air_freight_rate.models.air_freight_location_cluster_mapping import (
    AirFreightLocationClusterMapping,
    AirFreightLocationClusters,
)
from micro_services.client import maps
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from playhouse.shortcuts import model_to_dict


def json_encoder_for_clickhouse(data):
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


class AirFreightWeightSlab(Connection):
    def __init__(self, rate_id, validity_id, lower_limit, upper_limit) -> None:
        super().__init__()
        self.rate_id = None
        self.validity_id = None
        self.lower_limit = None
        self.upper_limit = None
        self.air_freight_rate_statistics_identifier = None
        self.set_identifier_details(rate_id, validity_id, lower_limit, upper_limit)

    def update_row_status_to_stale_and_return_new_row(self, row) -> dict:
        row = AirFreightRateStatistic(**row)
        new_row_dict = model_to_dict(row)
        row.sign = -1
        row.save(force_insert=True)
        new_row_dict["version"] += 1
        return new_row_dict

    def get_postgres_statistics_current_row_by_identifier(self) -> Model:
        return (
            AirFreightRateStatistic.select()
            .where(
                AirFreightRateStatistic.identifier
                == self.air_freight_rate_statistics_identifier,
                AirFreightRateStatistic.sign == 1,
            )
            .first()
        )



    def get_clickhouse_statistics_current_row_by_identifier(self) -> dict:
        parameters = {
            "table": Table.air_freight_rate_statistics.value,
            "identifier": self.air_freight_rate_statistics_identifier,
            "sign": 1,
        }
        if row := self.clickhouse_client.query(
            "SELECT * FROM brahmastra.{table:Identifier} WHERE identifier = {identifier:FixedString(256)} and sign = {sign:Int8}",
            parameters,
        ):
            if rows := get_clickhouse_rows_with_column_names(row):
                return rows[0]




    def set_identifier_details(self, rate_id, validity_id, lower_limit, upper_limit) -> None:
        self.rate_id = rate_id
        self.validity_id = validity_id
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit
        self.fcl_freight_rate_statistics_identifier = "_".join([rate_id, validity_id, str(lower_limit), str(upper_limit)])



    def create_stats(self, create_param) -> Model:
        return AirFreightRateStatistic.create(**create_param)

    def update_stats(self, new_params=dict(), return_new_row_without_updating=True):
        old_row = self.get_postgres_statistics_current_row_by_identifier()

        if old_row:
            if return_new_row_without_updating:
                return old_row
            for k, v in new_params.items():
                setattr(old_row, k, v)
                old_row.save()
        else:
            old_row = self.get_clickhouse_statistics_current_row_by_identifier()
            if not old_row:
                return
            row = self.update_row_status_to_stale_and_return_new_row(old_row)
            if return_new_row_without_updating:
                return row

            if new_params:
                new_params["id"] = row["id"]
                self.create_stats(new_params)


class Rate:
    def __init__(self, freight) -> None:
        self.freight = freight
        self.params = []
        self.origin_pricing_zone_map_id = None
        self.destination_pricing_zone_map_id = None
        self.origin_region_id = None
        self.destination_region_id = None
        self.set_non_existing_location_details()

    def set_new_stats(self) -> int:
        return AirFreightRateStatistic.insert_many(self.params).execute()

    def set_existing_stats(self) -> None:
        if self.params:
            air_freight_weight_slab = AirFreightWeightSlab(
                rate_id=self.params[0]["rate_id"],
                validity_id=self.params[0]["validity_id"],
                lower_limit=self.params[0]["lower_limit"],
                upper_limit=self.params[0]["upper_limit"]
            )

        for i, new_row in enumerate(self.params):
            # we dont want to run this in async so we just make one connection for one rate
            if i:
                air_freight_weight_slab.set_identifier_details(
                    rate_id=new_row["rate_id"],
                    validity_id=new_row["validity_id"],
                    lower_limit=new_row["lower_limit"],
                    upper_limit=new_row["upper_limit"]
                )
            if new_row["last_action"] == ValidityAction.create.value:
                air_freight_weight_slab.create_stats(new_row)
            elif new_row["last_action"] == ValidityAction.update.value:
                air_freight_weight_slab.update_stats(new_row)
            elif new_row["last_action"] == ValidityAction.unchanged.value:
                continue

    def set_non_existing_location_details(self) -> None:
        (
            self.origin_pricing_zone_map_id,
            self.destination_pricing_zone_map_id,
        ) = self.get_pricing_map_zone_ids(self.freight.origin_airport_id, self.freight.destination_airport_id)
        origin, destination = self.get_missing_location_ids(
            self.freight.origin_airport_id, self.freight.destination_airport_id
        )

        self.origin_region_id = origin.get("region_id")
        self.destination_region_id = destination.get("region_id")

    def set_formatted_data(self) -> None:
        freight = self.freight.dict(exclude={"validities", "weight_slabs"})

        for validity in self.freight.validities:
            for weight_slab in validity.weight_slabs:
                param = freight.copy()
                param.update(validity.dict(exclude={"weight_slabs"}))
                param["identifier"] = "_".join(
                    [
                        param["rate_id"],
                        param["validity_id"],
                        str(weight_slab.lower_limit),
                        str(weight_slab.upper_limit)
                    ]
                )
                param["price"] = weight_slab.tariff_price
                param["lower_limit"] = weight_slab.lower_limit
                param["upper_limit"] = weight_slab.upper_limit
                param["origin_pricing_zone_map_id"] = self.origin_pricing_zone_map_id
                param[
                    "destination_pricing_zone_map_id"
                ] = self.destination_pricing_zone_map_id
                param["origin_region_id"] = self.origin_region_id
                param["destination_region_id"] = self.destination_region_id
                self.params.append(param)

    def get_pricing_map_zone_ids(self, origin_airport_id, destination_airport_id) -> list:
        query = (
            AirFreightLocationClusters.select(
                AirFreightLocationClusterMapping.location_id,
                AirFreightLocationClusters.map_zone_id,
            )
            .join(AirFreightLocationClusterMapping)
            .where(
                AirFreightLocationClusterMapping.location_id.in_(
                    [origin_airport_id, destination_airport_id]
                )
            )
        )
        map_zone_location_mapping = jsonable_encoder(
            {item["location_id"]: item["map_zone_id"] for item in query.dicts()}
        )
        return map_zone_location_mapping.get(
            origin_airport_id
        ), map_zone_location_mapping.get(destination_airport_id)

    def get_missing_location_ids(self, origin_airport_id, destination_airport_id):
        response = maps.list_locations(
            data={
                "filters": {"id": [origin_airport_id, destination_airport_id]},
                "includes": {"region_id": True, "id": True},
            }
        )
        if "list" in response and len(response["list"]) == 2:
            region_id_mapping = {
                item["id"]: dict(
                    region_id=item["region_id"]
                )
                for item in response["list"]
            }
            return region_id_mapping.get(origin_airport_id), region_id_mapping.get(
                destination_airport_id
            )
        return None, None