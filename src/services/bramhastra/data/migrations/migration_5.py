from services.fcl_freight_rate.models.fcl_freight_rate_audit import FclFreightRateAudit
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from playhouse.postgres_ext import ServerSide
from configs.definitions import ROOT_DIR
import pandas as pd
from services.bramhastra.enums import Fcl
from pathlib import Path
from services.bramhastra.client import json_encoder_for_clickhouse, ClickHouse
from micro_services.client import common
from services.bramhastra.models.fcl_freight_rate_audit_statistic import (
    FclFreightRateAuditStatistic,
)
from database.create_clicks import Clicks
from services.rate_sheet.interactions.upload_file import upload_media_file
from joblib import delayed, Parallel, cpu_count
from datetime import datetime, timedelta


def generate_batch_intervals():
    start_date_str = "2023-04-01"
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.now()
    batch_intervals = []

    current_date = start_date
    while current_date <= end_date:
        batch_intervals.append(
            {"fro": current_date, "to": current_date + timedelta(days=14)}
        )
        current_date += timedelta(days=15)

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


path = Path(f"{ROOT_DIR}/services/bramhastra/data/migrations/temp")

path.mkdir(parents=True, exist_ok=True)

PATH = str(path)

KEYS_TO_KEEP = ["code", "currency", "price", "unit"]

clicks = Clicks(models=[FclFreightRateAuditStatistic], ignore_oltp=True)


clicks.delete()
clicks.create()

COLUMNS = [field for field in FclFreightRateAuditStatistic._meta.fields.keys()]

FIELDS = ",".join(COLUMNS)

def main():
    p = ParallelJobs()

    p.parallel_function(generate_batch_intervals(), execute)

def execute(date):
    fro = date.get("fro")
    to = date.get("to")

    csv_path = (
        PATH
        + f"""/{fro.strftime("%Y-%m-%d")}_{to.strftime("%Y-%m-%d")}_fcl.csv""".strip()
    )

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
            FclFreightRateAudit.object_id.alias("rate_id")
        )
        .where(
            FclFreightRateAudit.updated_at >= fro,
            FclFreightRateAudit.updated_at <= to,
            FclFreightRateAudit.object_type == "FclFreightRate",
            FclFreightRateAudit.action_name.in_(["create", "update"]),
        )
        .join(FclFreightRate, on=(FclFreightRateAudit.object_id == FclFreightRate.id))
    )

    rows = []

    for audit in ServerSide(query.dicts()):
        audit = json_encoder_for_clickhouse(audit)

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

            audit_row = {k: audit_row[k] for k in COLUMNS if k != "id"}

            audits.append(audit_row)

        rows.extend(audits)

    if not rows:
        return

    df = pd.DataFrame(columns=COLUMNS, data=rows)

    df.to_csv(csv_path, index=False)

    url = upload_media_file(csv_path)

    clickhouse = ClickHouse()

    query = f"INSERT INTO brahmastra.{FclFreightRateAuditStatistic._meta.table_name} SETTINGS async_insert=1, wait_for_async_insert=1 SELECT {FIELDS} FROM s3('{url}')"

    clickhouse.execute(query)

if __name__ == "__main__":
    main()
    path.rmdir()
