from celery_worker import celery

from services.fcl_cfs_rate.workers.update_fcl_cfs_rate_jobs_to_backlog import (
    update_fcl_cfs_rate_jobs_to_backlog,
)
from celery.schedules import crontab
from services.fcl_cfs_rate.interaction.create_fcl_cfs_rate_job import create_fcl_cfs_rate_job

tasks = {
    'update_fcl_cfs_jobs_status_to_backlogs': {
        'task': 'services.fcl_cfs_rate.fcl_cfs_celery_worker.update_fcl_cfs_rate_jobs_to_backlog_delay',
        'schedule': crontab(hour=23, minute=0),
        'options': {'queue': 'fcl_freight_rate'}
    },
}

for name, task_info in tasks.items():
    celery.conf.beat_schedule[name] = task_info
        
@celery.task(bind=True, max_retries=1, retry_backoff=True)
def update_fcl_cfs_rate_jobs_to_backlog_delay(self):
    try:
        return update_fcl_cfs_rate_jobs_to_backlog()
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)
        
@celery.task(bind = True, max_retries=1, retry_backoff = True)
def create_jobs_for_fcl_cfs_rate_request_delay(self, requirements):
    try:
        return create_fcl_cfs_rate_job(requirements, "rate_request")
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)