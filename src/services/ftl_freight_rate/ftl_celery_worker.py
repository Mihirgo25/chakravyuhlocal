from celery_worker import celery
from services.ftl_freight_rate.helpers.ftl_freight_rate_helpers import adding_multiple_service_object
from services.ftl_freight_rate.interactions.create_ftl_freight_rate import create_ftl_freight_rate
from services.ftl_freight_rate.workers.update_ftl_freight_rate_jobs_to_backlog import update_ftl_freight_rate_jobs_to_backlog
from services.ftl_freight_rate.interactions.create_ftl_freight_rate_job import update_live_booking_visiblity_for_ftl_freight_rate_job
from services.ftl_freight_rate.workers.update_ftl_freight_rate_job_on_rate_addition import update_ftl_freight_rate_job_on_rate_addition
from services.ftl_freight_rate.helpers.ftl_freight_rate_helpers import create_ftl_freight_rate_distance

from celery.schedules import crontab

tasks = {
    'update_ftl_freight_jobs_status_to_backlogs': {
        'task': 'services.ftl_freight_rate.ftl_celery_worker.update_ftl_freight_rate_jobs_to_backlog_delay',
        'schedule': crontab(hour=22, minute=30),
        'options': {'queue': 'fcl_freight_rate'}
    },
}

for name, task_info in tasks.items():
    celery.conf.beat_schedule[name] = task_info


@celery.task(bind = True, max_retries=5, retry_backoff = True)
def bulk_operation_perform_action_functions(self, action_name,object,sourced_by_id,procured_by_id):
    try:
        eval(f"object.perform_{action_name}_action(sourced_by_id='{sourced_by_id}',procured_by_id='{procured_by_id}')")
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, max_retries=5, retry_backoff = True)
def delay_ftl_functions(self,request):
    try:
       adding_multiple_service_object(request)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, max_retries=5, retry_backoff = True)
def update_ftl_freight_rate_request_delay(self, request):
    from services.ftl_freight_rate.interactions.update_ftl_freight_rate_request import update_ftl_freight_rate_request
    try:
        update_ftl_freight_rate_request(request)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, max_retries=1, retry_backoff = True)
def send_missing_or_dislike_rate_notifications_to_kam(self, object, request):
    try:
        object.send_missing_or_dislike_rate_notifications_to_kam(request.get('query_raised_by_id'), request.get('is_rate_missing_or_dislike'))
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, max_retries=1, retry_backoff = True)
def send_missing_or_dislike_rate_notifications_to_platform(self, object, request):
    try:
        object.send_missing_or_dislike_rate_notifications_to_platform(request.get('query_raised_by_id'), request.get('is_rate_missing_or_dislike'))
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)
        
@celery.task(bind = True, max_retries=3, retry_backoff=True)
def create_ftl_freight_rate_delay(self, request):
    try:
        return create_ftl_freight_rate(request)
    except Exception as e:
        if type(e).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= e)
        
@celery.task(bind=True, max_retries=1, retry_backoff=True)
def update_ftl_freight_rate_jobs_to_backlog_delay(self):
    try:
        return update_ftl_freight_rate_jobs_to_backlog()
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)

@celery.task(bind=True, max_retries=1, retry_backoff=True)
def update_live_booking_visiblity_for_ftl_freight_rate_job_delay(self, job_id):
    try:
        return update_live_booking_visiblity_for_ftl_freight_rate_job(job_id)
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)

@celery.task(bind=True, max_retries=1, retry_backoff=True)
def update_ftl_freight_rate_job_on_rate_addition_delay(self, request, id):
    try:
        return update_ftl_freight_rate_job_on_rate_addition(request, id)
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)
        
@celery.task(bind=True, max_retries=1, retry_backoff=True)
def create_ftl_freight_rate_distance_delay(self,ftl_object,request):
    try:
        return create_ftl_freight_rate_distance(ftl_object,request)
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)