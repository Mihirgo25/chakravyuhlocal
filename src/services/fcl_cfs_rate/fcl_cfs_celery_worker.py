from celery_worker import celery

from services.fcl_cfs_rate.workers.update_fcl_cfs_rate_jobs_to_backlog import (
    update_fcl_cfs_rate_jobs_to_backlog,
)
from services.fcl_cfs_rate.interaction.create_fcl_cfs_rate_job import update_live_booking_visiblity_for_fcl_cfs_rate_job
from services.fcl_cfs_rate.workers.update_fcl_cfs_rate_job_on_rate_addition import update_fcl_cfs_rate_job_on_rate_addition
from celery.schedules import crontab

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

@celery.task(bind=True, max_retries=1, retry_backoff=True)
def update_live_booking_visiblity_for_fcl_cfs_rate_job_delay(self, job_id):
    try:
        return update_live_booking_visiblity_for_fcl_cfs_rate_job(job_id)
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)

@celery.task(bind=True, max_retries=1, retry_backoff=True)
def update_fcl_cfs_rate_job_on_rate_addition_delay(self, request, id):
    try:
        return update_fcl_cfs_rate_job_on_rate_addition(request, id)
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)

from services.fcl_cfs_rate.helpers.update_organization_fcl_cfs import update_organization_fcl_cfs
from celery_worker import celery
from services.fcl_cfs_rate.interaction.update_fcl_cfs_rate_platform_prices import update_fcl_cfs_rate_platform_prices

@celery.task(bind = True, max_retries=5, retry_backoff = True)
def send_notifications_to_supply_agents_cfs_request_delay(self, object):
    try:
        object.send_notifications_to_supply_agents()
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)
        

@celery.task(bind = True, max_retries=5, retry_backoff = True)
def fcl_cfs_functions_delay(self,fcl_cfs_object,request):
    try:
        update_organization_fcl_cfs(request)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)
        
@celery.task(bind = True, max_retries=5, retry_backoff = True)
def update_fcl_cfs_rate_platform_prices_delay(self, request):
    try:
        update_fcl_cfs_rate_platform_prices(request)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)
        
@celery.task(bind = True, retry_backoff=True, max_retries=5)
def create_fcl_cfs_rate_delay(self, request):
    from services.fcl_cfs_rate.interaction.create_fcl_cfs_rate import create_fcl_cfs_rate
    try:
        return create_fcl_cfs_rate(request)
    except Exception as e:
        if type(e).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= e)
        

@celery.task(bind = True, max_retries=5, retry_backoff = True)
def send_notifications_to_supply_agents_cfs_feedback_delay(self, object, request):
    try:
        object.send_notifications_to_supply_agents(request)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, max_retries=5, retry_backoff = True)
def send_notifications_to_sales_agent_fcl_cfs_feedback_delay(self, object):
    try:
        object.send_closed_notifications_to_sales_agent()
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)