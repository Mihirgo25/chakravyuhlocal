from celery_worker import celery

from services.fcl_freight_rate.workers.update_fcl_freight_rate_jobs_to_backlog import (
    update_fcl_freight_rate_jobs_to_backlog,
)
from services.fcl_freight_rate.workers.update_fcl_freight_rate_job_on_rate_addition import (
    update_fcl_freight_rate_job_on_rate_addition,
)
from services.fcl_freight_rate.workers.create_jobs_for_predicted_fcl_freight_rate import create_jobs_for_predicted_fcl_freight_rate
from services.fcl_freight_rate.workers.create_sailing_schedule_port_pair_coverage import create_sailing_schedules_port_pair_coverages
from celery.schedules import crontab
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_job import update_live_booking_visiblity_for_fcl_freight_rate_job
from configs.fcl_freight_rate_constants import DEFAULT_RATE_TYPE
from services.fcl_freight_rate.interaction.send_fcl_freight_rate_task_notification import send_fcl_freight_rate_task_notification
from services.fcl_freight_rate.interaction.extend_create_fcl_freight_rate import extend_create_fcl_freight_rate_data
from services.fcl_freight_rate.interaction.create_fcl_freight_rate import create_fcl_freight_rate_data
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.interaction.delete_fcl_freight_rate_request import delete_fcl_freight_rate_request
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_free_day import create_fcl_freight_rate_free_day
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_local import create_fcl_freight_rate_local
from services.fcl_freight_rate.interaction.add_local_rates_on_country import add_local_rates_on_country
from services.fcl_freight_rate.helpers.fcl_freight_rates_to_cogo_assured_helper import fcl_freight_rates_to_cogo_assured_helper
from services.envision.interaction.create_fcl_freight_rate_prediction_feedback import create_fcl_freight_rate_prediction_feedback
from services.fcl_freight_rate.interaction.update_cogo_assured_fcl_freight_rate_validities import update_cogo_assured_fcl_freight_rate_validities
from services.fcl_freight_rate.interaction.update_fcl_freight_rate_request import update_fcl_freight_rate_request
from services.fcl_freight_rate.interaction.update_fcl_freight_rate_feedback import update_fcl_freight_rate_feedback
from services.fcl_freight_rate.helpers.cluster_extension_by_latest_trends_helper import cluster_extension_by_latest_trends_helper

from services.fcl_freight_rate.interaction.create_fcl_freight_rate_local_job import (
    update_live_booking_visiblity_for_fcl_freight_rate_local_job
)
from services.fcl_freight_rate.workers.update_fcl_freight_rate_local_jobs_to_backlog import (
    update_fcl_freight_rate_local_jobs_to_backlog
)
from services.fcl_freight_rate.workers.update_fcl_freight_rate_local_job_on_rate_addition import (
    update_fcl_freight_rate_local_job_on_rate_addition,
)
from micro_services.client import organization
import concurrent.futures

tasks = {
    'update_fcl_freight_jobs_status_to_backlogs': {
        'task': 'services.fcl_freight_rate.fcl_celery_worker.update_fcl_freight_rate_jobs_to_backlog_delay',
        'schedule': crontab(hour=22, minute=5),
        'options': {'queue': 'fcl_freight_rate'}
    },
}

for name, task_info in tasks.items():
    celery.conf.beat_schedule[name] = task_info

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
        return update_fcl_freight_rate_job_on_rate_addition(request, id)
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)
        
@celery.task(bind=True, max_retries=3, retry_backoff=True)
def update_fcl_freight_rate_jobs_to_backlog_delay(self):
    try:
        return update_fcl_freight_rate_jobs_to_backlog()
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)
        
        
@celery.task(bind=True, max_retries=1, retry_backoff=True)
def update_live_booking_visiblity_for_fcl_freight_rate_job_delay(self, job_id):
    try:
        return update_live_booking_visiblity_for_fcl_freight_rate_job(job_id)
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)
   
     
@celery.task(bind = True, max_retries=5, retry_backoff = True)
def create_sailing_schedule_port_pair_coverage_delay (self,request):
    try:
        return create_sailing_schedules_port_pair_coverages(request)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, max_retries=5, retry_backoff = True)
def create_fcl_freight_rate_delay(self, request):
    try:
        return create_fcl_freight_rate_data(request)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)


@celery.task(bind = True, max_retries=5, retry_backoff = True)
def delay_fcl_functions(self, request):
    try:
        if not FclFreightRate.select().where(FclFreightRate.service_provider_id==request["service_provider_id"], FclFreightRate.rate_not_available_entry==False, FclFreightRate.rate_type == DEFAULT_RATE_TYPE).exists():
            organization.update_organization({'id':request.get("service_provider_id"), "freight_rates_added":True})

        if request.get("fcl_freight_rate_request_id"):
            delete_fcl_freight_rate_request(request)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, max_retries=5, retry_backoff = True)
def send_fcl_freight_rate_task_notifications(self, task_id):
    try:
        send_fcl_freight_rate_task_notification(task_id)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, retry_backoff=True, max_retries=5)
def celery_create_fcl_freight_rate_free_day(self, request):
    try:
        return create_fcl_freight_rate_free_day(request)
    except Exception as e:
        if type(e).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= e)


@celery.task(bind = True, retry_backoff=True, max_retries=5)
def celery_extend_create_fcl_freight_rate_data(self, request):
    try:
        return extend_create_fcl_freight_rate_data(request)
    except Exception as e:
        if type(e).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= e)

@celery.task(bind = True, retry_backoff=True, max_retries=5)
def celery_create_fcl_freight_rate_local(self, request):
    try:
        return create_fcl_freight_rate_local(request)
    except Exception as e:
        if type(e).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= e)

@celery.task(bind = True, retry_backoff=True,max_retries=1)
def fcl_freight_rates_to_cogo_assured(self):
    try:
        fcl_freight_rates_to_cogo_assured_helper()
    except Exception as exc:
        pass


@celery.task(bind = True, retry_backoff=True,max_retries=5)
def create_fcl_freight_rate_feedback_for_prediction(self, result):
    try:
        create_fcl_freight_rate_prediction_feedback(result)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, retry_backoff = True, max_retries = 3)
def create_country_wise_locals_in_delay(self, request):
    try:
        add_local_rates_on_country(request)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)



@celery.task(bind = True, max_retries=5, retry_backoff = True)
def fcl_freight_local_data_updation(self, request):
    try:
        params = {
        'performed_by_id': request['performed_by_id'],
        'organization_id': request['service_provider_id'],
        'port_id': request['port_id'],
        'trade_type': request['trade_type']
        }
        organization.create_organization_serviceable_port(params)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind=True, retry_backoff=True, max_retries=1)
def update_cogo_assured_fcl_freight_rates(self):
    batch_size = 5000
    cogo_assured_rates = FclFreightRate.select().where(FclFreightRate.rate_type == 'cogo_assured').order_by(FclFreightRate.updated_at.desc())
    total_size = cogo_assured_rates.count()
    for batch in range(0, total_size, batch_size):
        batched_rates = cogo_assured_rates.limit(batch_size).offset(batch)
        if not batched_rates.exists():
            break

        batch_rates = list(batched_rates.dicts())
        with concurrent.futures.ThreadPoolExecutor(max_workers = 4) as executor:
            futures = [executor.submit(update_cogo_assured_fcl_freight_rate_validities, rate) for rate in batch_rates]


@celery.task(bind = True, retry_backoff=True,max_retries=5)
def update_fcl_freight_rate_request_in_delay(self, request):
    try:
        update_fcl_freight_rate_request(request)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, retry_backoff=True,max_retries=3)
def update_fcl_freight_rate_feedback_in_delay(self, request):
    try:
        update_fcl_freight_rate_feedback(request)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True,retry_backoff=True,max_retries=3)
def cluster_extension_by_latest_trends_worker(self):
    try:
        cluster_extension_by_latest_trends_helper()
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc) @celery.task(bind=True, max_retries=1, retry_backoff=True)

def update_fcl_freight_rate_local_jobs_to_backlog_delay(self):
    try:
        return update_fcl_freight_rate_local_jobs_to_backlog()
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)
        
@celery.task(bind=True, max_retries=1, retry_backoff=True)
def update_live_booking_visiblity_for_fcl_freight_rate_local_job_delay(self, job_id):
    try:
        return update_live_booking_visiblity_for_fcl_freight_rate_local_job(job_id)
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)
        
@celery.task(bind=True, max_retries=1, retry_backoff=True)
def update_fcl_freight_rate_local_job_on_rate_addition_delay(self, request, id):
    try:
        return update_fcl_freight_rate_local_job_on_rate_addition(request, id)
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)