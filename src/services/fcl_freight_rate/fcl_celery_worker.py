from celery_worker import celery


from services.fcl_freight_rate.workers.update_fcl_freight_job_status import (
    update_fcl_freight_job_status,
)
from services.fcl_freight_rate.workers.update_fcl_freight_rate_job_on_rate_addition import (
    update_fcl_freight_rate_job_on_rate_addition,
)
from services.fcl_freight_rate.workers.create_jobs_for_predicted_fcl_freight_rate import create_jobs_for_predicted_fcl_freight_rate
from celery.schedules import crontab




@celery.task(bind = True, max_retries=5, retry_backoff = True)
def create_jobs_for_predicted_fcl_freight_rate_delay(self, is_predicted, requirements):
    try:
        return create_jobs_for_predicted_fcl_freight_rate(is_predicted, requirements)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)


@celery.task(bind=True, max_retries=1, retry_backoff=True)
def update_fcl_freight_rate_job_on_rate_addition_delay(self, request, id):
    try:
        update_fcl_freight_rate_job_on_rate_addition(request, id)
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)
        

@celery.task(bind=True, max_retries=3, retry_backoff=True)
def update_fcl_freight_job_status_delay(self):
    try:
        update_fcl_freight_job_status()
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)
        

