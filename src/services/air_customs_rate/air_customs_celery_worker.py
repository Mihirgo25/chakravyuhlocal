from celery_worker import celery
from services.air_customs_rate.helpers.update_organization_air_customs import update_organization_air_customs
from services.air_customs_rate.interaction.create_air_customs_rate import create_air_customs_rate
from services.air_customs_rate.workers.update_air_customs_rate_jobs_to_backlog import (
    update_air_customs_rate_jobs_to_backlog,
)
from services.air_customs_rate.workers.update_air_customs_rate_job_on_rate_addition import (
    update_air_customs_rate_job_on_rate_addition,
)
from services.air_customs_rate.interaction.create_air_customs_rate_job import update_live_booking_visiblity_for_air_customs_rate_job

from celery.schedules import crontab

tasks = {
    'update_air_customs_jobs_status_to_backlogs': {
        'task': 'services.air_customs_rate.air_customs_celery_worker.update_air_customs_rate_jobs_to_backlog_delay',
        'schedule': crontab(hour=22, minute=25),
        'options': {'queue': 'fcl_freight_rate'}
    },
}

for name, task_info in tasks.items():
    celery.conf.beat_schedule[name] = task_info

@celery.task(bind = True, retry_backoff=True, max_retries=5)
def air_customs_functions_delay(self,air_customs_object,request):
    try:
        update_organization_air_customs(request)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, retry_backoff = True, max_retries=5)
def bulk_operation_perform_action_functions_air_customs_delay(self, action_name, object):
    try:
        eval(f"object.perform_{action_name}_action()")
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, retry_backoff=True, max_retries=5)
def create_air_customs_rate_delay(self, request):
    try:
        return create_air_customs_rate(request)
    except Exception as e:
        if type(e).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= e)
        
@celery.task(bind = True, retry_backoff=True, max_retries=5)
def send_closed_notifications_to_sales_agent_air_customs_delay(self, object):
    try:
        object.send_closed_notifications_to_sales_agent()
    except Exception as e:
        if type(e).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= e)

        
@celery.task(bind=True, max_retries=1, retry_backoff=True)
def update_air_customs_rate_job_on_rate_addition_delay(self, request, id):
    try:
        return update_air_customs_rate_job_on_rate_addition(request, id)
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)
        
@celery.task(bind=True, max_retries=1, retry_backoff=True)
def update_air_customs_rate_jobs_to_backlog_delay(self):
    try:
        return update_air_customs_rate_jobs_to_backlog()
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)

@celery.task(bind=True, max_retries=1, retry_backoff=True)
def update_live_booking_visiblity_for_air_customs_rate_job_delay(self, job_id):
    try:
        return update_live_booking_visiblity_for_air_customs_rate_job(job_id)
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)