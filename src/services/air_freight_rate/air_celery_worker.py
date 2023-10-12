from celery_worker import celery
from services.air_freight_rate.workers.create_jobs_for_predicted_air_freight_rate import (
    create_jobs_for_predicted_air_freight_rate,
)
from services.air_freight_rate.workers.update_air_freight_rate_jobs_to_backlog import (
    update_air_freight_rate_jobs_to_backlog,
)
from services.air_freight_rate.workers.update_air_freight_rate_job_on_rate_addition import (
    update_air_freight_rate_job_on_rate_addition,
)
from services.air_freight_rate.interactions.create_air_freight_rate_job import create_air_freight_rate_job
from celery.schedules import crontab
from services.air_freight_rate.workers.update_air_freight_rate_local_jobs_to_backlog import update_air_freight_rate_local_jobs_to_backlog
from services.air_freight_rate.interactions.create_air_freight_rate_job import update_live_booking_visiblity_for_air_freight_rate_job


tasks = {
    'update_air_freight_jobs_status_to_backlogs': {
        'task': 'services.air_freight_rate.air_celery_worker.update_air_freight_rate_jobs_to_backlog_delay',
        'schedule': crontab(hour=22, minute=10),
        'options': {'queue': 'fcl_freight_rate'}
    },
    'update_air_freight_local_jobs_status_to_backlogs': {
        'task': 'services.air_freight_rate.air_celery_worker.update_air_freight_rate_local_jobs_to_backlog_delay',
        'schedule': crontab(hour=22, minute=55),
        'options': {'queue': 'fcl_freight_rate'}
    },
}

for name, task_info in tasks.items():
    celery.conf.beat_schedule[name] = task_info


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
def update_air_freight_rate_job_on_rate_addition_delay(self, request, id):
    try:
        return update_air_freight_rate_job_on_rate_addition(request, id)
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)
        
@celery.task(bind=True, max_retries=1, retry_backoff=True)
def update_air_freight_rate_jobs_to_backlog_delay(self):
    try:
        return update_air_freight_rate_jobs_to_backlog()
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)


@celery.task(bind = True, max_retries=5, retry_backoff = True)
def create_jobs_for_air_freight_rate_request_delay(self, requirements):
    try:
        return create_air_freight_rate_job(requirements, "rate_request")
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)
        

@celery.task(bind = True, max_retries=5, retry_backoff = True)
def create_jobs_for_air_freight_rate_feedback_delay(self, requirements):
    try:
        return create_air_freight_rate_job(requirements, "rate_feedback")
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)
        
        
@celery.task(bind=True, max_retries=1, retry_backoff=True)
def update_live_booking_visiblity_for_air_freight_rate_job_delay(self, job_id):
    try:
        return update_live_booking_visiblity_for_air_freight_rate_job(job_id)
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)
        
@celery.task(bind=True, max_retries=1, retry_backoff=True)
def update_air_freight_rate_local_jobs_to_backlog_delay(self):
    try:
        return update_air_freight_rate_local_jobs_to_backlog()
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)