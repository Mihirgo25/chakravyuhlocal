from services.chakravyuh.models.worker_log import WorkerLog
from peewee import SQL
from datetime import datetime, timedelta
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.interaction.update_fcl_rates_to_cogo_assured import (
    update_fcl_rates_to_cogo_assured,
)
import concurrent.futures
from configs.fcl_freight_rate_constants import DEFAULT_RATE_TYPE
from playhouse.postgres_ext import ServerSide


def fcl_freight_rates_to_cogo_assured_helper():
    start_time = datetime.utcnow()
    row = {
        "module_name": "fcl_freight_rates_to_cogo_assured",
        "module_type": "function",
    }

    worker = (
        WorkerLog.select()
        .where(
            WorkerLog.module_name == "fcl_freight_rates_to_cogo_assured",
            WorkerLog.module_type == "function",
        )
        .first()
    )

    if not worker:
        last_updated_at = datetime.utcnow() - timedelta(hours=5)
        row["started_at"] = datetime.utcnow()
        worker = WorkerLog.create(**row)
    else:
        if worker.status == 'started':
            return True
        
        last_updated_at = worker.last_updated_at
        worker.started_at = start_time
        worker.ended_at = None
        worker.last_updated_at = datetime.utcnow()
        worker.status = 'started'
        worker.save()

    try:
        query = FclFreightRate.select(
            FclFreightRate.origin_port_id,
            FclFreightRate.origin_main_port_id,
            FclFreightRate.destination_port_id,
            FclFreightRate.destination_main_port_id,
            FclFreightRate.container_size,
            FclFreightRate.container_type,
            FclFreightRate.commodity,
        ).where(
            FclFreightRate.mode.not_in(["predicted", "cluster_extension"]),
            FclFreightRate.updated_at >= last_updated_at,
            FclFreightRate.validities != SQL("'[]'"),
            ~FclFreightRate.rate_not_available_entry,
            FclFreightRate.container_size << ["20", "40", "40HC"],
            FclFreightRate.rate_type == DEFAULT_RATE_TYPE,
        )
        grouped_set = set()

        for rate in ServerSide(query):
            grouped_set.add(
                f'{str(rate.origin_port_id)}:{str(rate.origin_main_port_id or "")}:{str(rate.destination_port_id)}:{str(rate.destination_main_port_id or "")}:{str(rate.container_size)}:{str(rate.container_type)}:{str(rate.commodity)}'
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(execute_update_fcl_rates_to_cogo_assured, key)
                for key in grouped_set
            ]
        worker.ended_at = datetime.utcnow()
        worker.status = 'completed'
        worker.save()
    except:
        worker.ended_at = datetime.utcnow()
        worker.status = 'failed'
        worker.save()
        
    
    


def execute_update_fcl_rates_to_cogo_assured(key):
    (
        origin_port_id,
        origin_main_port_id,
        destination_port_id,
        destination_main_port_id,
        container_size,
        container_type,
        commodity,
    ) = key.split(":")
    param = {
        "origin_port_id": origin_port_id,
        "origin_main_port_id": None if not origin_main_port_id else origin_main_port_id,
        "destination_port_id": destination_port_id,
        "destination_main_port_id": None
        if not destination_main_port_id
        else destination_main_port_id,
        "container_size": container_size,
        "container_type": container_type,
        "commodity": commodity,
    }
    update_fcl_rates_to_cogo_assured(param)
