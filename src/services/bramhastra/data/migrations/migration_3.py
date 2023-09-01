from configs.env import *
from services.bramhastra.client import ClickHouse
from services.bramhastra.models.air_freight_rate_statistic import (
    AirFreightRateStatistic,
)
from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)
from services.chakravyuh.models.worker_log import WorkerLog
from database.db_migration import run_migration
from services.bramhastra.constants import INDIAN_LOCATION_ID
from datetime import datetime
from services.bramhastra.enums import BrahmastraTrackModuleTypes, BrahmastraTrackStatus


def main():
    print("running migration")

    run_migration()

    click = ClickHouse()

    click.execute("drop database brahmastra")

    click.execute("create database brahmastra")

    from database.create_clicks import Clicks

    Clicks(
        models=[AirFreightRateStatistic, FclFreightRateStatistic], ignore_oltp=True
    ).create()

    WorkerLog.delete().execute()

    print("started inserting fcl")

    execute_fcl(click)

    print("started inserting air")

    execute_air(click)

    print("completed")


def execute_fcl(click):
    started_at = datetime.utcnow()
    columns = [field for field in FclFreightRateStatistic._meta.fields.keys()]
    fields = ",".join(columns)
    click.execute(
        f"INSERT INTO brahmastra.{FclFreightRateStatistic._meta.table_name} SETTINGS async_insert=1, wait_for_async_insert=1 SELECT {fields} FROM postgresql('{DATABASE_HOST}:{DATABASE_PORT}', '{DATABASE_NAME}', '{FclFreightRateStatistic._meta.table_name}', '{DATABASE_USER}', '{DATABASE_PASSWORD}') WHERE rate_type != 'cogo_assured'"
    )
    print("done cogoassured")
    click.execute(
        f"INSERT INTO brahmastra.{FclFreightRateStatistic._meta.table_name} SETTINGS async_insert=1, wait_for_async_insert=1 SELECT {fields} FROM postgresql('{DATABASE_HOST}:{DATABASE_PORT}', '{DATABASE_NAME}', '{FclFreightRateStatistic._meta.table_name}', '{DATABASE_USER}', '{DATABASE_PASSWORD}') WHERE rate_type = 'cogo_assured' AND origin_country_id = '{INDIAN_LOCATION_ID}'"
    )
    print("done cogo assured origin india")
    click.execute(
        f"INSERT INTO brahmastra.{FclFreightRateStatistic._meta.table_name} SETTINGS async_insert=1, wait_for_async_insert=1 SELECT {fields} FROM postgresql('{DATABASE_HOST}:{DATABASE_PORT}', '{DATABASE_NAME}', '{FclFreightRateStatistic._meta.table_name}', '{DATABASE_USER}', '{DATABASE_PASSWORD}') WHERE rate_type = 'cogo_assured' AND origin_country_id != '{INDIAN_LOCATION_ID}'"
    )
    print("done cogo assured non origin india")

    params = {
        "name": "brahmastra",
        "module_name": FclFreightRateStatistic._meta.table_name,
        "module_type": BrahmastraTrackModuleTypes.table.value,
        "last_updated_at": started_at,
        "started_at": started_at,
        "status": BrahmastraTrackStatus.completed.value,
        "ended_at": datetime.utcnow(),
    }

    WorkerLog.create(**params)


def execute_air(click):
    started_at = datetime.utcnow()
    columns = [field for field in AirFreightRateStatistic._meta.fields.keys()]
    fields = ",".join(columns)
    for source in ["manual", "predicted", "rate_extension", "rate_sheet"]:
        click.execute(
            f"INSERT INTO brahmastra.{AirFreightRateStatistic._meta.table_name} SETTINGS async_insert=1, wait_for_async_insert=1 SELECT {fields} FROM postgresql('{DATABASE_HOST}:{DATABASE_PORT}', '{DATABASE_NAME}', '{AirFreightRateStatistic._meta.table_name}', '{DATABASE_USER}', '{DATABASE_PASSWORD}') WHERE source = %(source)s",
            {"source": source}
        )
        print("done with source: ", source)

    params = {
        "name": "brahmastra",
        "module_name": AirFreightRateStatistic._meta.table_name,
        "module_type": BrahmastraTrackModuleTypes.table.value,
        "last_updated_at": started_at,
        "started_at": started_at,
        "status": BrahmastraTrackStatus.completed.value,
        "ended_at": datetime.utcnow(),
    }

    WorkerLog.create(**params)


if __name__ == "__main__":
    main()
