from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)
from services.bramhastra.client import ClickHouse, json_encoder_for_clickhouse
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
from playhouse.postgres_ext import ServerSide
import pandas as pd
from services.bramhastra.constants import DEFAULT_UUID
from services.rate_sheet.interactions.upload_file import upload_media_file
from services.bramhastra.constants import BRAHMASTRA_CSV_FILE_PATH
from services.bramhastra.enums import (
    ImportTypes,
    AppEnv,
    BrahmastraTrackStatus,
    BrahmastraTrackModuleTypes,
)
from services.chakravyuh.models.worker_log import WorkerLog
import sentry_sdk
from services.bramhastra.models.air_freight_rate_statistic import (
    AirFreightRateStatistic,
)
import os

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
        self.models = models or [FclFreightRateStatistic, AirFreightRateStatistic]
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
            if getattr(row, key):
                params[key] = str(getattr(row, key))
            else:
                params[key] = DEFAULT_UUID
            where.append(f"{key} = %({key})s")

        old_row = self.__clickhouse.execute(
            f"SELECT * from brahmastra.{model._meta.table_name} WHERE {' AND '.join(where)}",
            params,
        )

        if old_row:
            old_row[0]["sign"] = -1
            return old_row[0]

    def __create_brahmastra_track(
        self, model, status, started_at, last_updated_at=None, ended_at=None
    ):
        params = {
            "name": "brahmastra",
            "module_name": model._meta.table_name,
            "module_type": BrahmastraTrackModuleTypes.table.value,
            "last_updated_at": last_updated_at,
            "started_at": started_at,
            "status": status,
            "ended_at": ended_at,
        }
        return WorkerLog.create(**params)

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
            brahmastra_track = self.get_track(model)

            try:
                query = (
                    model.select(model.updated_at)
                    .where(model.updated_at > brahmastra_track.last_updated_at)
                    .order_by(model.updated_at.desc())
                    .limit(1)
                    .first()
                )

                if not query:
                    brahmastra_track.status = BrahmastraTrackStatus.empty.value
                    brahmastra_track.ended_at = datetime.utcnow()
                    brahmastra_track.save()
                    return

                new_last_updated_at = query.updated_at

                rows = []
                count = 0
                for row in ServerSide(
                    model.select().where(model.updated_at >= brahmastra_track.last_updated_at)
                ):
                    print(count)
                    count += 1
                    data = json_encoder_for_clickhouse(
                        {field: getattr(row, field) for field in columns}
                    )

                    if old_data := self.__get_clickhouse_row(model, row):
                        data["version"] = old_data["version"] + 1
                        rows.append(json_encoder_for_clickhouse(old_data))

                    rows.append(data)

                dataframe = pd.DataFrame(data=rows)

                file_path = BRAHMASTRA_CSV_FILE_PATH

                dataframe.to_csv(file_path, index=False)

                url = upload_media_file(file_path)
                
                try:
                    os.remove(file_path)
                except Exception:
                    pass

                query = f"INSERT INTO brahmastra.{model._meta.table_name} SETTINGS async_insert=1, wait_for_async_insert=1 SELECT {fields} FROM s3('{url}')"
                
                breakpoint()

                self.__clickhouse.execute(query)

                status = BrahmastraTrackStatus.completed.value

                brahmastra_track.last_updated_at = new_last_updated_at
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
        # if APP_ENV == AppEnv.production.value:
            self.on_startup = on_startup

            for model in self.models:
                self.__build_query_and_insert_to_clickhouse(model)
                if arjun:
                    self.__optimize_and_send_data_to_stale_tables(
                        model, pass_to_stale=False
                    )

                print(f"done with {model._meta.table_name}")

    def get_track(self, model):
        if (
            track := WorkerLog.select()
            .where(
                WorkerLog.module_name == model._meta.table_name,
                WorkerLog.module_type == BrahmastraTrackModuleTypes.table.value,
            )
            .order_by(WorkerLog.ended_at.desc())
            .limit(1)
            .first()
        ):
            return track
