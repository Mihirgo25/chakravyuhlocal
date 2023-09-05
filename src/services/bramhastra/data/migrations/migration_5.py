from services.fcl_freight_rate.models.fcl_freight_rate_audit import FclFreightRateAudit
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from playhouse.postgres_ext import ServerSide
from services.bramhastra.enums import Fcl
from services.bramhastra.client import ClickHouse
from micro_services.client import common
from services.bramhastra.models.fcl_freight_rate_audit_statistic import (
    FclFreightRateAuditStatistic,
)
from configs.env import *
from database.create_clicks import Clicks
from joblib import delayed, Parallel, cpu_count
from datetime import datetime, timedelta
from database.db_support import get_db


def generate_batch_intervals():
    start_date_str = "2023-07-01"
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime("2023-09-30", "%Y-%m-%d")
    batch_intervals = []

    current_date = start_date
    while current_date <= end_date:
        batch_intervals.append(
            {"fro": current_date, "to": current_date + timedelta(days=2)}
        )
        current_date += timedelta(days=3)
        
    # batch_intervals = [{
    #     "fro": datetime.strptime("2023-07-01", "%Y-%m-%d"),
    #     "to": datetime.strptime("2023-09-30", "%Y-%m-%d")
    # }]

    return batch_intervals


class ParallelJobs:
    def __init__(self):
        self.count_of_cpus = cpu_count()
        self.verbose = 100

    def parallel_function(self, parallel_list, function_call):
        parallel_pool = Parallel(
            n_jobs=self.count_of_cpus, prefer="threads", verbose=self.verbose
        )
        functions = [delayed(function_call)(each) for each in parallel_list]
        res = parallel_pool(functions)
        return res


KEYS_TO_KEEP = ["code", "currency", "price", "unit"]

COLUMNS = [field for field in FclFreightRateAuditStatistic._meta.fields.keys()]

FIELDS = ",".join(COLUMNS)

global counter
counter = 1


def reset():
    clicks = Clicks(models=[FclFreightRateAuditStatistic])
 
    try:
        FclFreightRateAuditStatistic._meta.database.execute_sql(f"drop table {FclFreightRateAuditStatistic._meta.table_name}")
    except:
        pass
    
    clicks.delete()

    clicks.create()


def main(db = get_db()):
    
    reset()
    
    p = ParallelJobs()

    batches = generate_batch_intervals()
    
    for batch in batches:
        execute(batch)

    print(
        "------------------------- SENDING TO CLICKHOUSE -------------------------------"
    )

    send_to_clickhouse()


def execute(date):
    fro = date.get("fro")
    to = date.get("to")

    query = (
        FclFreightRateAudit.select(
            FclFreightRate.origin_continent_id,
            FclFreightRate.destination_continent_id,
            FclFreightRate.origin_country_id,
            FclFreightRate.destination_country_id,
            FclFreightRate.origin_port_id,
            FclFreightRate.destination_port_id,
            FclFreightRate.cogo_entity_id,
            FclFreightRate.shipping_line_id,
            FclFreightRate.service_provider_id,
            FclFreightRate.commodity,
            FclFreightRate.container_size,
            FclFreightRate.container_type,
            FclFreightRate.importer_exporter_id,
            FclFreightRateAudit.action_name,
            FclFreightRateAudit.performed_by_id,
            FclFreightRateAudit.performed_by_type,
            FclFreightRateAudit.data,
            FclFreightRateAudit.created_at,
            FclFreightRateAudit.object_id.alias("rate_id"),
        )
        .where(
            FclFreightRateAudit.created_at >= fro,
            FclFreightRateAudit.created_at <= to,
            FclFreightRateAudit.object_type == "FclFreightRate",
            FclFreightRateAudit.action_name.in_(["create", "update"]),
        )
        .join(FclFreightRate, on=(FclFreightRateAudit.object_id == FclFreightRate.id))
    )

    rows = []

    for audit in ServerSide(query.dicts()):
        audits = []

        data = audit.get("data", {})

        audit["validity_start"] = data.get("validity_start")
        audit["validity_end"] = data.get("validity_end")
        audit["sourced_by_id"] = data.get("sourced_by_id")
        audit["procured_by_id"] = data.get("procured_by_id")

        if not data:
            continue

        del audit["data"]

        line_items = data.get("line_items", [])
        if not line_items:
            continue

        for line_item in line_items:
            audit_row = audit.copy()
            for key in KEYS_TO_KEEP:
                if key not in line_item:
                    del line_item[key]
            if line_item["currency"] == Fcl.default_currency.value:
                line_item["standard_price"] = line_item["price"]
            else:
                line_item["standard_price"] = common.get_money_exchange_for_fcl(
                    {
                        "from_currency": line_item["currency"],
                        "to_currency": Fcl.default_currency.value,
                        "price": line_item["price"],
                    }
                ).get("price", line_item["price"])

            audit_row.update(line_item)

            for key in COLUMNS:
                if key not in COLUMNS:
                    del audit_row[key]
                    
            global counter

            audit_row["id"] = counter

            audit_row = {k: audit_row.get(k) for k in COLUMNS}

            audits.append(audit_row)

            counter += 1

        rows.extend(audits)
        
        if len(rows) >= 20000:
            FclFreightRateAuditStatistic.insert_many(rows).execute()
            rows = []
                

    if rows:
        FclFreightRateAuditStatistic.insert_many(rows).execute()


def send_to_clickhouse():
    click = ClickHouse()

    columns = [field for field in FclFreightRateAuditStatistic._meta.fields.keys()]
    fields = ",".join(columns)

    BATCH_SIZE = 100000

    min = 1
    max = BATCH_SIZE

    total_count = FclFreightRateAuditStatistic.select(
        FclFreightRateAuditStatistic.id
    ).count()

    while True:
        click.execute(
            f"INSERT INTO brahmastra.{FclFreightRateAuditStatistic._meta.table_name} SETTINGS async_insert=1, wait_for_async_insert=1 SELECT {fields} FROM postgresql('{DATABASE_HOST}:{DATABASE_PORT}', '{DATABASE_NAME}', '{FclFreightRateAuditStatistic._meta.table_name}', '{DATABASE_USER}', '{DATABASE_PASSWORD}') WHERE id <= {max} AND id >= {min}"
        )

        print(f"Done from {min} to {max} where total is {total_count}")

        min += BATCH_SIZE
        max += BATCH_SIZE

        if max > total_count:
            break

    click.execute(
        f"INSERT INTO brahmastra.{FclFreightRateAuditStatistic._meta.table_name} SETTINGS async_insert=1, wait_for_async_insert=1 SELECT {fields} FROM postgresql('{DATABASE_HOST}:{DATABASE_PORT}', '{DATABASE_NAME}', '{FclFreightRateAuditStatistic._meta.table_name}', '{DATABASE_USER}', '{DATABASE_PASSWORD}') WHERE id > {min}"
    )

    print(f"sending remaing data")


if __name__ == "__main__":
    main()
