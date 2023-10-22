from celery_worker import celery
from services.haulage_freight_rate.helpers.haulage_freight_rate_helpers import adding_multiple_service_object
from services.haulage_freight_rate.interactions.update_haulage_freight_rate_request import update_haulage_freight_rate_request
from services.haulage_freight_rate.interactions.create_haulage_freight_rate import create_haulage_freight_rate
from services.haulage_freight_rate.interactions.update_haulage_freight_rate_platform_prices import update_haulage_freight_rate_platform_prices
from services.haulage_freight_rate.workers.create_jobs_for_predicted_haulage_freight_rate import create_jobs_for_predicted_haulage_freight_rate
from services.haulage_freight_rate.workers.update_haulage_freight_rate_job_on_rate_addition import (
    update_haulage_freight_rate_job_on_rate_addition,
)
from services.haulage_freight_rate.workers.update_haulage_freight_rate_jobs_to_backlog import (
    update_haulage_freight_rate_jobs_to_backlog,
)
from services.haulage_freight_rate.interactions.create_haulage_freight_rate_job import update_live_booking_visiblity_for_haulage_freight_rate_job


from celery.schedules import crontab

tasks = {
    'update_haulage_freight_jobs_status_to_backlogs': {
        'task': 'services.haulage_freight_rate.haulage_celery_worker.update_haulage_freight_rate_jobs_to_backlog_delay',
        'schedule': crontab(hour=22, minute=15),
        'options': {'queue': 'fcl_freight_rate'}
    },
}

for name, task_info in tasks.items():
    celery.conf.beat_schedule[name] = task_info
    
@celery.task(bind = True, max_retries=3, retry_backoff = True)    
def bulk_operation_perform_action_functions_haulage(self, action_name,object,sourced_by_id,procured_by_id):
    try:
        eval(f"object.perform_{action_name}_action(sourced_by_id='{sourced_by_id}',procured_by_id='{procured_by_id}')")
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)
        
@celery.task(bind = True, max_retries=3, retry_backoff = True)
def update_haulage_freight_rate_request_delay(self, request):
    try:
        update_haulage_freight_rate_request(request)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)
        

@celery.task(bind = True, max_retries=3, retry_backoff = True)
def delay_haulage_functions(self,request):
    try:
       adding_multiple_service_object(request)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)


@celery.task(bind = True, max_retries=3, retry_backoff=True)
def create_haulage_freight_rate_delay(self, request):
    try:
        return create_haulage_freight_rate(request)
    except Exception as e:
        if type(e).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= e)



@celery.task(bind = True, max_retries=1, retry_backoff = True)
def update_haulage_rate_platform_prices_delay(self, request):
    try:
        update_haulage_freight_rate_platform_prices(request)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)
        
@celery.task(bind = True, max_retries=1, retry_backoff = True)
def create_jobs_for_predicted_haulage_freight_rate_delay(self, is_predicted, requirements):
    try:
        return create_jobs_for_predicted_haulage_freight_rate(is_predicted, requirements)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)
        
@celery.task(bind=True, max_retries=1, retry_backoff=True)
def update_haulage_freight_rate_job_on_rate_addition_delay(self, request, id):
    try:
        return update_haulage_freight_rate_job_on_rate_addition(request, id)
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)


@celery.task(bind=True, max_retries=1, retry_backoff=True)
def update_haulage_freight_rate_jobs_to_backlog_delay(self):
    try:
        return update_haulage_freight_rate_jobs_to_backlog()
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)
        
@celery.task(bind=True, max_retries=1, retry_backoff=True)
def update_live_booking_visiblity_for_haulage_freight_rate_job_delay(self, job_id):
    try:
        return update_live_booking_visiblity_for_haulage_freight_rate_job(job_id)
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)
        