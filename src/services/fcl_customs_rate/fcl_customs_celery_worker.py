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
from services.fcl_customs_rate.interaction.create_fcl_customs_rate_job import update_live_booking_visiblity_for_fcl_customs_rate_job
from celery.schedules import crontab
from services.fcl_customs_rate.interaction.update_fcl_customs_rate_platform_prices import update_fcl_customs_rate_platform_prices
from services.fcl_customs_rate.interaction.create_fcl_customs_rate import create_fcl_customs_rate
from services.fcl_customs_rate.helpers.update_organization_fcl_customs import update_organization_fcl_customs

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
        
@celery.task(bind=True, max_retries=1, retry_backoff=True)
def update_live_booking_visiblity_for_fcl_customs_rate_job_delay(self, job_id):
    try:
        return update_live_booking_visiblity_for_fcl_customs_rate_job(job_id)
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)

@celery.task(bind = True, max_retries=5, retry_backoff = True)
def update_fcl_customs_rate_platform_prices_delay(self, request):
    try:
        update_fcl_customs_rate_platform_prices(request)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)
        

@celery.task(bind = True, retry_backoff=True, max_retries=5)
def create_fcl_customs_rate_delay(self, request):
    try:
        return create_fcl_customs_rate(request)
    except Exception as e:
        if type(e).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= e)

@celery.task(bind = True, max_retries=5, retry_backoff = True)
def fcl_customs_functions_delay(self,fcl_customs_object,request):
    try:
        update_organization_fcl_customs(request)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)
