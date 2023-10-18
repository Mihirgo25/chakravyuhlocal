from celery_worker import celery

from services.lcl_customs_rate.workers.update_lcl_customs_rate_jobs_to_backlog import (
    update_lcl_customs_rate_jobs_to_backlog,
)
from services.lcl_customs_rate.interactions.create_lcl_customs_rate_job import update_live_booking_visiblity_for_lcl_customs_rate_job
from celery.schedules import crontab

tasks = {
    'update_lcl_customs_jobs_status_to_backlogs': {
        'task': 'services.lcl_customs_rate.lcl_customs_celery_worker.update_lcl_customs_rate_jobs_to_backlog_delay',
        'schedule': crontab(hour=22, minute=45),
        'options': {'queue': 'fcl_freight_rate'}
    },
}

for name, task_info in tasks.items():
    celery.conf.beat_schedule[name] = task_info

@celery.task(bind=True, max_retries=1, retry_backoff=True)
def update_lcl_customs_rate_jobs_to_backlog_delay(self):
    try:
        return update_lcl_customs_rate_jobs_to_backlog()
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)
        
@celery.task(bind=True, max_retries=1, retry_backoff=True)
def update_live_booking_visiblity_for_lcl_customs_rate_job_delay(self, job_id):
    try:
        return update_live_booking_visiblity_for_lcl_customs_rate_job(job_id)
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)