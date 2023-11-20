from peewee import SQL
from datetime import datetime, timedelta
from services.chakravyuh.models.worker_log import WorkerLog
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.interaction.calc_fcl_freight_rate_estimation_ratio import fcl_freight_rate_estimation_ratio



def fcl_freight_rate_estimation_ratio_helper():
    start_time = datetime.utcnow()
    row = {
        "module_name": "fcl_freight_rate_estimation_ratio",
        "module_type": "function",
        "name": "fcl_freight_rate_estimation_ratio"
    }

    worker = (
        WorkerLog.select()
        .where(
            WorkerLog.module_name == "fcl_freight_rate_estimation_ratio",
            WorkerLog.module_type == "function",
            WorkerLog.name == "fcl_freight_rate_estimation_ratio",
        )
        .first()
    )

    if not worker:
        row["started_at"] = datetime.utcnow()
        worker = WorkerLog.create(**row)
    else:
        worker.started_at = start_time
        worker.ended_at = None
        worker.last_updated_at = datetime.utcnow()
        worker.status = 'started'
        worker.save()

    try:
        fcl_freight_rate_estimation_ratio()
        worker.ended_at = datetime.utcnow()
        worker.status = 'completed'
        worker.save()
    except:
        worker.ended_at = datetime.utcnow()
        worker.status = 'failed'
        worker.save()
        
