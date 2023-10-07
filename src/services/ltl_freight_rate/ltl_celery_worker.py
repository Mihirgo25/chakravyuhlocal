from celery_worker import celery

from services.ltl_freight_rate.workers.update_ltl_freight_rate_jobs_to_backlog import (
    update_ltl_freight_rate_jobs_to_backlog,
)
from celery.schedules import crontab

tasks = {
    'update_ltl_freight_jobs_status_to_backlogs': {
        'task': 'services.ltl_freight_rate.ltl_celery_worker.update_ltl_freight_rate_jobs_to_backlog_delay',
        'schedule': crontab(hour=22, minute=35),
        'options': {'queue': 'fcl_freight_rate'}
    },
}

for name, task_info in tasks.items():
    celery.conf.beat_schedule[name] = task_info

@celery.task(bind=True, max_retries=1, retry_backoff=True)
def update_ltl_freight_rate_jobs_to_backlog_delay(self):
    try:
        return update_ltl_freight_rate_jobs_to_backlog()
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)