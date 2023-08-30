from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)
from services.bramhastra.client import ClickHouse
import peewee
from configs.env import (
    DATABASE_HOST,
    DATABASE_NAME,
    DATABASE_PASSWORD,
    DATABASE_PORT,
    DATABASE_USER,
    APP_ENV,
)
from datetime import datetime
from database.db_session import rd
from playhouse.postgres_ext import ServerSide
import pandas as pd
from services.bramhastra.constants import DEFAULT_UUID
from fastapi.encoders import jsonable_encoder
from services.rate_sheet.interactions.upload_file import upload_media_file
from services.bramhastra.constants import BRAHMASTRA_CSV_FILE_PATH
from services.bramhastra.enums import ImportTypes, AppEnv, BrahmastraTrackStatus
from services.bramhastra.models.brahmastra_track import BrahmastraTrack
import sentry_sdk

"""
Info:
Brahmastra is a tool used to send statistics to ClickHouse for analytical queries.

Code:
Brahmastra(models).used_by(arjun=True)

Options:
If models are not send it will run for all available models present in the clickhouse system
If `arjun` is not the user, old duplicate entries won't be cleared. We recommend using `arjun` as user to clear these entries once in a while for better performance.
"""


class Brahmastra:
    def __init__(self, models: list[peewee.Model] = None) -> None:
        self.models = models or [FclFreightRateStatistic]
        self.__clickhouse = ClickHouse()
        self.on_startup = None

    def __optimize_and_send_data_to_stale_tables(
        self, model: peewee.Model, pass_to_stale: bool = True
    ):
        if self.on_startup:
            return

        if pass_to_stale:
            query = f"""
            INSERT INTO brahmastra.stale_{model._meta.table_name} SETTINGS async_insert=1, wait_for_async_insert=1 
            WITH LatestVersions AS (
                SELECT
                id,max(version)
                FROM
                brahmastra.{model._meta.table_name}
                GROUP BY id
            )
            SELECT * FROM brahmastra.{model._meta.table_name} WHERE (id, version) NOT IN (
            SELECT id,version
            FROM LatestVersions)"""
            self.__clickhouse.execute(query)
        self.__clickhouse.execute(f"OPTIMIZE TABLE brahmastra.{model._meta.table_name}")

    def __get_clickhouse_row(self, model, row):
        params = dict()
        where = []
        for key in model.CLICK_KEYS:
            if not getattr(row, key):
                params[key] = str(getattr(row, key))
            else:
                params[key] = DEFAULT_UUID
            where.append(f"%({key})s")

        query = (
            f"SELECT * from brahmastra.{model._meta.table_name} WHERE {','.join(where)}"
        )

        if row := self.__clickhouse.execute(query, params)[0]:
            row["version"] += 1
            row["sign"] = -1

            return row

    def __create_brahmastra_track(
        self, model, status, started_at, last_updated_at=None, ended_at=None
    ):
        return BrahmastraTrack.create(
            **{
                "table_name": model._meta.table_name,
                "last_updated_at": last_updated_at,
                "started_at": started_at,
                "status": status,
                "ended_at": ended_at,
            }
        )

    def __build_query_and_insert_to_clickhouse(self, model: peewee.Model):
        columns = [field for field in model._meta.fields.keys()]
        fields = ",".join(columns)
        status = BrahmastraTrackStatus.started.value
        started_at = datetime.utcnow()
        if self.on_startup:
            try:
                self.insert_directly_via_postgres(model, fields)
                status = BrahmastraTrackStatus.completed.value
            except Exception as e:
                print(e)
                sentry_sdk.capture_exception(e)
                status = BrahmastraTrackStatus.failed.value
            return self.__create_brahmastra_track(
                model, status, started_at, datetime.utcnow(), datetime.utcnow()
            ).id

        if model.IMPORT_TYPE == ImportTypes.csv.value:
            dataframe = pd.DataFrame(columns=columns)

            last_updated_at = self.get_last_updated_at(model)

            brahmastra_track = self.__create_brahmastra_track(
                model, status, datetime.utcnow()
            )

            try:
                brahmastra_track.last_updated_at = (
                    model.select(model.updated_at)
                    .where(model.updated_at >= last_updated_at)
                    .order_by(model.updated_at.desc())
                    .limit(1)
                    .first()
                    .updated_at
                )
                for row in ServerSide(
                    model.select(model.id).where(model.updated_at >= last_updated_at)
                ):
                    data = jsonable_encoder(
                        {field: getattr(row, field) for field in columns}
                    )

                    if old_data := self.__get_clickhouse_row(model, row):
                        data["version"] = old_data["version"] + 1
                        dataframe = dataframe.append(data, ignore_index=True)
                        model.update(version=data["version"]).where(
                            model.id == data.get("id")
                        ).execute()

                    dataframe = dataframe.append(old_data, ignore_index=True)

                dataframe.to_csv(BRAHMASTRA_CSV_FILE_PATH)
                url = upload_media_file(BRAHMASTRA_CSV_FILE_PATH)

                self.__clickhouse.execute(
                    f"INSERT INTO brahmastra.{model._meta.table_name} SETTINGS async_insert=1, wait_for_async_insert=1 SELECT {fields} FROM s3('{url}','CSV')"
                )
                status = BrahmastraTrackStatus.completed.value
            except Exception as e:
                print(e)
                sentry_sdk.capture_exception(e)
                status = BrahmastraTrackStatus.failed.value

            brahmastra_track.status = status
            brahmastra_track.ended_at = datetime.utcnow()

            brahmastra_track.save()

            return brahmastra_track.id

        elif model.IMPORT_TYPE == ImportTypes.postgres.value:
            self.insert_directly_via_postgres(model, fields)

    def insert_directly_via_postgres(self, model, fields):
        self.__clickhouse.execute(
            f"INSERT INTO brahmastra.{model._meta.table_name} SETTINGS async_insert=1, wait_for_async_insert=1 SELECT {fields} FROM postgresql('{DATABASE_HOST}:{DATABASE_PORT}', '{DATABASE_NAME}', '{model._meta.table_name}', '{DATABASE_USER}', '{DATABASE_PASSWORD}')"
        )

    def used_by(self, arjun: bool, on_startup: bool = False) -> None:
        if APP_ENV == AppEnv.production.value:
            self.on_startup = on_startup

            for model in self.models:
                self.__build_query_and_insert_to_clickhouse(model)
                if arjun:
                    self.__optimize_and_send_data_to_stale_tables(
                        model, pass_to_stale=False
                    )

                print(f"done with {model._meta.table_name}")

    def get_last_updated_at(self, model):
        if (
            track := BrahmastraTrack.select(BrahmastraTrack.last_updated_at)
            .where(
                BrahmastraTrack.last_updated_at != None,
                BrahmastraTrack.status == BrahmastraTrackStatus.completed.value,
                BrahmastraTrack.table_name == model._meta.table_name,
            )
            .order_by(FclFreightRateStatistic.created_at.desc())
            .limit(1)
            .first()
        ):
            return track.last_updated_at
