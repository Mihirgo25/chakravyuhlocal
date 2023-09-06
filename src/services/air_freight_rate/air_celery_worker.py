from celery_worker import celery
from services.air_freight_rate.workers.air_freight_cancelled_shipments_scheduler import (
    air_freight_cancelled_shipments_scheduler,
)
from services.air_freight_rate.workers.air_freight_critical_port_pairs_scheduler import (
    air_freight_critical_port_pairs_scheduler,
)
from services.air_freight_rate.workers.air_freight_expiring_rates_scheduler import (
    air_freight_expiring_rates_scheduler,
)
from services.air_freight_rate.workers.create_jobs_for_predicted_air_freight_rate import (
    create_jobs_for_predicted_air_freight_rate,
)
from services.air_freight_rate.workers.update_air_freight_job_status import (
    update_air_freight_job_status,
)
from services.air_freight_rate.interactions.update_air_freight_rate_job import (
    update_air_freight_rate_job,
)
from celery.schedules import crontab


tasks = {
    "air_cancelled_shipments": {
        "task": "services.air_freight_rate.air_celery_worker.air_freight_cancelled_shipments_in_delay",
        "schedule": crontab(hour=20, minute=50),
        "options": {"queue": "fcl_freight_rate"},
    },
    "air_freight_expiring_rates": {
        "task": "services.air_freight_rate.air_celery_worker.air_freight_expiring_rates_in_delay",
        "schedule": crontab(hour=17, minute=50),
        "options": {"queue": "fcl_freight_rate"},
    },
    "air_freight_critical_port_pairs": {
        "task": "services.air_freight_rate.air_celery_worker.air_freight_critical_port_pairs_delay",
        'schedule': crontab(hour=00, minute=50),
        "options": {"queue": "fcl_freight_rate"},
    },
    # 'update_air_job_status': {
    #     'task': 'services.air_freight_rate.air_celery_worker.update_air_freight_jobs_status_delay',
    #     'schedule': crontab(hour=18, minute=20),
    #     'options': {'queue': 'fcl_freight_rate'}
    #     }
}

for name, task_info in tasks.items():
    celery.conf.beat_schedule[name] = task_info


@celery.task(bind=True, retry_backoff=True, max_retries=1)
def air_freight_cancelled_shipments_in_delay(self):
    try:
        air_freight_cancelled_shipments_scheduler()
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)


@celery.task(bind=True, max_retries=1, retry_backoff=True)
def air_freight_critical_port_pairs_delay(self):
    try:
        air_freight_critical_port_pairs_scheduler()
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)


@celery.task(bind=True, retry_backoff=True, max_retries=1)
def air_freight_expiring_rates_in_delay(self):
    try:
        air_freight_expiring_rates_scheduler()
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)


@celery.task(bind=True, max_retries=1, retry_backoff=True)
def create_jobs_for_predicted_air_freight_rate_delay(
    self, is_predicted, requirements
):
    try:
        return create_jobs_for_predicted_air_freight_rate(
            is_predicted, requirements
        )
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)


@celery.task(bind=True, max_retries=1, retry_backoff=True)
def update_air_freight_jobs_status_delay(self):
    try:
        update_air_freight_job_status()
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)


@celery.task(bind=True, max_retries=1, retry_backoff=True)
def update_air_freight_rate_jobs_delay(self, request, id):
    try:
        update_air_freight_rate_job(request, id)
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)
