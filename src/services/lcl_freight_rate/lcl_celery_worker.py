from celery_worker import celery

from services.lcl_freight_rate.workers.update_lcl_freight_rate_jobs_to_backlog import (
    update_lcl_freight_rate_jobs_to_backlog,
)
from services.lcl_freight_rate.interactions.create_lcl_freight_rate_job import update_live_booking_visiblity_for_lcl_freight_rate_job
from services.lcl_freight_rate.workers.update_lcl_freight_rate_job_on_rate_addition import update_lcl_freight_rate_job_on_rate_addition
from celery.schedules import crontab

tasks = {
    'update_lcl_freight_jobs_status_to_backlogs': {
        'task': 'services.lcl_freight_rate.lcl_celery_worker.update_lcl_freight_rate_jobs_to_backlog_delay',
        'schedule': crontab(hour=22, minute=40),
        'options': {'queue': 'fcl_freight_rate'}
    },
}

for name, task_info in tasks.items():
    celery.conf.beat_schedule[name] = task_info

@celery.task(bind=True, max_retries=1, retry_backoff=True)
def update_lcl_freight_rate_jobs_to_backlog_delay(self):
    try:
        return update_lcl_freight_rate_jobs_to_backlog()
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)

@celery.task(bind=True, max_retries=1, retry_backoff=True)
def update_live_booking_visiblity_for_lcl_freight_rate_job_delay(self, job_id):
    try:
        return update_live_booking_visiblity_for_lcl_freight_rate_job(job_id)
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)

@celery.task(bind=True, max_retries=1, retry_backoff=True)
def update_lcl_freight_rate_job_on_rate_addition_delay(self, request, id):
    try:
        return update_lcl_freight_rate_job_on_rate_addition(request, id)
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)