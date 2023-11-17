from celery_worker import celery
from celery.schedules import crontab
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_local_job import (
    update_live_booking_visiblity_for_fcl_freight_rate_local_job
)
from services.fcl_freight_rate.workers.update_fcl_freight_rate_local_jobs_to_backlog import (
    update_fcl_freight_rate_local_jobs_to_backlog
)
from services.fcl_freight_rate.workers.update_fcl_freight_rate_local_job_on_rate_addition import (
    update_fcl_freight_rate_local_job_on_rate_addition,
)

tasks = {
    'update_fcl_freight_local_jobs_status_to_backlogs': {
        'task': 'services.fcl_freight_rate.fcl_celery_worker.update_fcl_freight_rate_local_jobs_to_backlog_delay',
        'schedule': crontab(hour=22, minute=50),
        'options': {'queue': 'fcl_freight_rate'}
    },
}

for name, task_info in tasks.items():
    celery.conf.beat_schedule[name] = task_info

@celery.task(bind=True, max_retries=1, retry_backoff=True)
def update_fcl_freight_rate_local_jobs_to_backlog_delay(self):
    try:
        return update_fcl_freight_rate_local_jobs_to_backlog()
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)
        
@celery.task(bind=True, max_retries=1, retry_backoff=True)
def update_live_booking_visiblity_for_fcl_freight_rate_local_job_delay(self, job_id):
    try:
        return update_live_booking_visiblity_for_fcl_freight_rate_local_job(job_id)
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)
        
@celery.task(bind=True, max_retries=1, retry_backoff=True)
def update_fcl_freight_rate_local_job_on_rate_addition_delay(self, request, id):
    try:
        return update_fcl_freight_rate_local_job_on_rate_addition(request, id)
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)
