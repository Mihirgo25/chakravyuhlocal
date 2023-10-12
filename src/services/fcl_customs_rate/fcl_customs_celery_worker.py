from celery_worker import celery


from services.fcl_customs_rate.workers.update_fcl_customs_rate_jobs_to_backlog import (
    update_fcl_customs_rate_jobs_to_backlog,
)
from services.fcl_customs_rate.workers.update_fcl_customs_rate_job_on_rate_addition import (
    update_fcl_customs_rate_job_on_rate_addition,
)
from services.fcl_customs_rate.workers.create_jobs_for_predicted_fcl_customs_rate import (
     create_jobs_for_predicted_fcl_customs_rate,
)
from services.fcl_customs_rate.interaction.create_fcl_customs_rate_job import (
    create_fcl_customs_rate_job,
)

from celery.schedules import crontab

tasks = {
    'update_fcl_customs_jobs_status_to_backlogs': {
        'task': 'services.fcl_customs_rate.fcl_customs_celery_worker.update_fcl_customs_rate_jobs_to_backlog_delay',
        'schedule': crontab(hour=22, minute=20),
        'options': {'queue': 'fcl_freight_rate'}
    },
}

for name, task_info in tasks.items():
    celery.conf.beat_schedule[name] = task_info


@celery.task(bind = True, max_retries=1, retry_backoff = True)
def create_jobs_for_predicted_fcl_customs_rate_delay(self, is_predicted, requirements):
    try:
        return create_jobs_for_predicted_fcl_customs_rate(is_predicted, requirements)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)


@celery.task(bind=True, max_retries=1, retry_backoff=True)
def update_fcl_customs_rate_job_on_rate_addition_delay(self, request, id):
    try:
        return update_fcl_customs_rate_job_on_rate_addition(request, id)
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)


@celery.task(bind=True, max_retries=1, retry_backoff=True)
def update_fcl_customs_rate_jobs_to_backlog_delay(self):
    try:
        return update_fcl_customs_rate_jobs_to_backlog()
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)
        
@celery.task(bind = True, max_retries=1, retry_backoff = True)
def create_jobs_for_fcl_customs_rate_feedback_delay(self, requirements):
    try:
        return create_fcl_customs_rate_job(requirements, "rate_feedback")
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, max_retries=1, retry_backoff = True)
def create_jobs_for_fcl_customs_rate_request_delay(self, requirements):
    try:
        return create_fcl_customs_rate_job(requirements, "rate_request")
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)