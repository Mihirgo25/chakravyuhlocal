from datetime import datetime
from services.bramhastra.models.fcl_freight_rate_request_statistics import (
    FclFreightRateRequestStatistic,
)
from services.bramhastra.enums import BrahmastraTrackModuleTypes, BrahmastraTrackStatus
from services.chakravyuh.models.worker_log import WorkerLog


def main():
    started_at = datetime.utcnow()
    params = {
        "name": "brahmastra",
        "module_name": FclFreightRateRequestStatistic._meta.table_name,
        "module_type": BrahmastraTrackModuleTypes.table.value,
        "last_updated_at": started_at,
        "started_at": started_at,
        "status": BrahmastraTrackStatus.empty.value,
        "ended_at": datetime.utcnow(),
    }

    WorkerLog.create(**params)


if __name__ == "__main__":
    main()
