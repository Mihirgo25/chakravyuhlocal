from celery_worker import celery

from services.fcl_freight_rate.workers.fcl_freight_critical_port_pairs_scheduler import (
    fcl_freight_critical_port_pairs_scheduler,
)
from services.fcl_freight_rate.workers.fcl_freight_cancelled_shipments_scheduler import (
    fcl_freight_cancelled_shipments_scheduler,
)
from services.fcl_freight_rate.workers.fcl_freight_expiring_rates_scheduler import (
    fcl_freight_expiring_rates_scheduler,
)
from services.fcl_freight_rate.workers.update_fcl_freight_job_status import (
    update_fcl_freight_job_status,
)
from services.fcl_freight_rate.interaction.update_fcl_freight_rate_job import (
    update_fcl_freight_rate_job,
)
from services.fcl_freight_rate.workers.create_jobs_for_predicted_fcl_freight_rate import create_jobs_for_predicted_fcl_freight_rate
from celery.schedules import crontab

tasks = {
    "fcl_cancelled_shipments": {
        "task": "services.fcl_freight_rate.fcl_celery_worker.fcl_freight_cancelled_shipments_in_delay",
        'schedule':crontab(hour=20, minute=30),
        "options": {"queue": "fcl_freight_rate"},
    },
    "fcl_freight_expiring_rates": {
        "task": "services.fcl_freight_rate.fcl_celery_worker.fcl_freight_expiring_rates_in_delay",
        "schedule": crontab(hour=17, minute=30),
        "options": {"queue": "fcl_freight_rate"},
    },
    "fcl_freight_critical_port_pairs": {
        "task": "services.fcl_freight_rate.fcl_celery_worker.fcl_freight_critical_port_pairs_delay",
        'schedule': crontab(hour=00, minute=30),
        "options": {"queue": "fcl_freight_rate"},
    },
    # 'update_fcl_job_status': {
    #     'task': 'celery_worker.update_fcl_freight_job_status_delay',
    #     'schedule': crontab(hour=18, minute=00),
    #     'options': {'queue': 'fcl_freight_rate'}
    # },
}

for name, task_info in tasks.items():
    celery.conf.beat_schedule[name] = task_info


@celery.task(bind=True, retry_backoff=True, max_retries=3)
def fcl_freight_cancelled_shipments_in_delay(self):
    try:
        fcl_freight_cancelled_shipments_scheduler()
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)


@celery.task(bind=True, retry_backoff=True, max_retries=3)
def fcl_freight_expiring_rates_in_delay(self):
    try:
        fcl_freight_expiring_rates_scheduler()
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)


@celery.task(bind=True, max_retries=3, retry_backoff=True)
def fcl_freight_critical_port_pairs_delay(self):
    try:
        fcl_freight_critical_port_pairs_scheduler()
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)


@celery.task(bind=True, max_retries=3, retry_backoff=True)
def update_fcl_freight_job_status_delay(self):
    try:
        update_fcl_freight_job_status()
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)


@celery.task(bind=True, max_retries=1, retry_backoff=True)
def update_fcl_freight_rate_jobs_delay(self, request, id):
    try:
        update_fcl_freight_rate_job(request, id)
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)
        

@celery.task(bind = True, max_retries=5, retry_backoff = True)
def create_jobs_for_predicted_fcl_freight_rate_delay(self, is_predicted, requirements):
    try:
        return create_jobs_for_predicted_fcl_freight_rate(is_predicted, requirements)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

