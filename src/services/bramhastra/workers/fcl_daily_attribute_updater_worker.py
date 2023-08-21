from services.fcl_freight_rate.models.fcl_freight_rate_audit import FclFreightRateAudit
from datetime import datetime, timedelta
from services.bramhastra.client import ClickHouse
from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)


class FclDailyAttributeUpdaterWorker:
    def __init__(self) -> None:
        self.clickhouse = ClickHouse()

    def execute(self):
        if fcl_freight_rate_audits := list(
            FclFreightRateAudit.select(
                FclFreightRateAudit.object_id.alias("rate_id"),
                FclFreightRateAudit.extended_from_object_id.alias("parent_rate_id"),
                FclFreightRateAudit.rate_sheet_id,
                FclFreightRateAudit.bulk_operation_id
            )
            .where(
                FclFreightRateAudit.created_at
                > datetime.utcnow() - timedelta(hours=27),
                FclFreightRateAudit.object_type == "FclFreightRate",
                FclFreightRateAudit.action_name == "create",
            )
            .dicts()
        ):
            for audit in fcl_freight_rate_audits:
                queries = f"ALTER TABLE brahmastra.{FclFreightRateStatistic._meta.table_name} UPDATE parent_rate_id = %(parent_rate_id)s WHERE (id,version) IN (SELECT id, MAX(version) AS max_version FROM brahmastra.{FclFreightRateStatistic._meta.table_name} WHERE rate_id = %(rate_id)s GROUP BY id)"
                self.clickhouse.execute(" ".join(queries), audit)
