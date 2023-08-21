from services.fcl_freight_rate.models.fcl_freight_rate_audit import FclFreightRateAudit
from datetime import datetime, timedelta
from services.bramhastra.client import ClickHouse
from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)
from fastapi.encoders import jsonable_encoder
from playhouse.postgres_ext import ServerSide
import sentry_sdk


class FclDailyAttributeUpdaterWorker:
    def __init__(self) -> None:
        self.clickhouse = ClickHouse()

    def execute(self):
        try:
            keys = {"parent_rate_id", "rate_sheet_id", "bulk_operation_id"}

            query = FclFreightRateAudit.select(
                FclFreightRateAudit.object_id.alias("rate_id"),
                FclFreightRateAudit.extended_from_object_id.alias("parent_rate_id"),
                FclFreightRateAudit.rate_sheet_id,
                FclFreightRateAudit.bulk_operation_id,
            ).where(
                FclFreightRateAudit.created_at
                > datetime.utcnow() - timedelta(hours=27),
                FclFreightRateAudit.object_type == "FclFreightRate",
                FclFreightRateAudit.action_name == "create",
            )
            for fcl_freight_rate_audit in ServerSide(query):
                query = [
                    f"ALTER TABLE brahmastra.{FclFreightRateStatistic._meta.table_name}"
                ]

                audit = dict(rate_id=fcl_freight_rate_audit.rate_id)
                update = []
                for key in keys:
                    if getattr(fcl_freight_rate_audit, key):
                        update.append(f"{key} = %({key})s")
                        audit[key] = getattr(fcl_freight_rate_audit, key)
                if len(audit) == 1:
                    continue

                query.append("UPDATE")

                query.append(",".join(update))
                query.append(
                    f"WHERE (id,version) IN (SELECT id, MAX(version) AS max_version FROM brahmastra.{FclFreightRateStatistic._meta.table_name} WHERE rate_id = %(rate_id)s GROUP BY id)"
                )
                self.clickhouse.execute(f" ".join(query), jsonable_encoder(audit))

        except Exception as e:
            sentry_sdk.capture_exception(e)
