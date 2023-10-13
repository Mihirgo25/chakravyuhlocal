from services.fcl_freight_rate.models.fcl_freight_rate_audit import FclFreightRateAudit
from datetime import datetime, timedelta
from services.bramhastra.client import ClickHouse
from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)
from playhouse.postgres_ext import ServerSide
import sentry_sdk
from services.chakravyuh.models.worker_log import WorkerLog
from services.bramhastra.enums import BrahmastraTrackModuleTypes, BrahmastraTrackStatus


class FclDailyAttributeUpdaterWorker:
    def __init__(self) -> None:
        self.clickhouse = ClickHouse()

    def execute(self):
        try:
            last_worker_execution_time = worker_log.last_updated_at
            worker_log = (
                WorkerLog.select()
                .where(
                    WorkerLog.module_type == BrahmastraTrackModuleTypes.function.value,
                    WorkerLog.module_name == 'FclDailyAttributeUpdaterWorker',
                )
                .first()
            )
            worker_log.started_time = datetime.utcnow()
            worker_log.ended_at = None
            worker_log.status = BrahmastraTrackStatus.started.value
            worker_log.last_updated_at = datetime.utcnow()
            worker_log.save()
            keys = {
                "parent_rate_id",
                "rate_sheet_id",
                "bulk_operation_id",
                "performed_by_id",
                "performed_by_type",
                "source",
            }

            query = FclFreightRateAudit.select(
                FclFreightRateAudit.object_id.alias("rate_id"),
                FclFreightRateAudit.extended_from_object_id.alias("parent_rate_id"),
                FclFreightRateAudit.rate_sheet_id,
                FclFreightRateAudit.bulk_operation_id,
                FclFreightRateAudit.created_at,
                FclFreightRateAudit.action_name,
                FclFreightRateAudit.performed_by_id,
                FclFreightRateAudit.performed_by_type,
                FclFreightRateAudit.source,
            ).where(
                FclFreightRateAudit.created_at >= last_worker_execution_time,
                FclFreightRateAudit.object_type == "FclFreightRate",
            )
            for fcl_freight_rate_audit in ServerSide(query):
                params = dict()
                for key in keys:
                    if getattr(fcl_freight_rate_audit, key):
                        params[key] = getattr(fcl_freight_rate_audit, key)

                if not params:
                    continue

                if fcl_freight_rate_audit.action_name != "create":
                    params["updated_at"] = fcl_freight_rate_audit.created_at

                fcl = (
                    FclFreightRateStatistic.update(**params)
                    .where(
                        FclFreightRateStatistic.rate_id
                        == fcl_freight_rate_audit.rate_id
                    )
                    .execute()
                )

            worker_log.status = BrahmastraTrackStatus.completed.value
            worker_log.ended_at = datetime.utcnow()
            worker_log.save()

        except Exception as e:
            worker_log.status = BrahmastraTrackStatus.failed.value
            worker_log.last_updated_at = last_worker_execution_time
            worker_log.save()
            print(e)
            sentry_sdk.capture_exception(e)
