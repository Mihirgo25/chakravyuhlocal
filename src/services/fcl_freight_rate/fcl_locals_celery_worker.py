from celery_worker import celery

from services.fcl_freight_rate.interaction.create_fcl_freight_rate_local_job import (
    create_fcl_freight_rate_local_job,
)
from services.fcl_freight_rate.interaction.delete_fcl_freight_rate_local_job import (
    delete_fcl_freight_rate_local_job,
)


@celery.task(bind=True, max_retries=5, retry_backoff=True)
def create_jobs_for_feedback_fcl_freight_rate_local_delay(self, requirements):
    try:
        return create_fcl_freight_rate_local_job(requirements, "rate_feedback")
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)


@celery.task(bind=True, max_retries=5, retry_backoff=True)
def create_jobs_for_request_fcl_freight_rate_local_delay(self, requirements):
    try:
        return create_fcl_freight_rate_local_job(requirements, "rate_request")
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)


@celery.task(bind=True, max_retries=5, retry_backoff=True)
def delete_jobs_for_fcl_freight_rate_local_delay(self, requirements):
    try:
        return delete_fcl_freight_rate_local_job(requirements)
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)
