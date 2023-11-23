from celery_worker import celery
from services.chakravyuh.interaction.get_air_invoice_estimation_prediction import invoice_rates_updation
from services.extensions.interactions.create_freight_look_rates import create_air_freight_rate_api
from services.air_freight_rate.interactions.create_air_freight_rate_local import create_air_freight_rate_local
from services.air_freight_rate.interactions.create_air_freight_rate import create_air_freight_rate
from services.air_freight_rate.interactions.create_air_freight_rate_surcharge import create_air_freight_rate_surcharge
from services.air_freight_rate.helpers.create_saas_air_schedule_helper import create_saas_air_schedule_airport_pair
from services.air_freight_rate.interactions.send_air_freight_rate_task_notification import send_air_freight_rate_task_notification
from services.air_freight_rate.workers.send_air_freight_local_charges_update_reminder_notification import send_air_freight_local_charges_update_reminder_notification
from services.air_freight_rate.workers.send_expired_air_freight_rate_notification import send_expired_air_freight_rate_notification
from services.air_freight_rate.workers.send_near_expiry_air_freight_rate_notification import send_near_expiry_air_freight_rate_notification
from services.air_freight_rate.helpers.air_freight_rate_card_helper import get_rate_from_cargo_ai
from services.air_freight_rate.interactions.update_air_freight_rate_request import update_air_freight_rate_request
from services.envision.interaction.create_air_freight_rate_prediction_feedback import create_air_freight_rate_feedback
from services.air_freight_rate.estimators.relate_airlines import RelateAirline

from services.chakravyuh.producer_vyuhs.air_freight import AirFreightVyuh as AirFreightVyuhProducer

from services.chakravyuh.setters.air_freight import AirFreightVyuh as AirFreightVyuhSetter

from services.air_freight_rate.workers.create_jobs_for_predicted_air_freight_rate import (
    create_jobs_for_predicted_air_freight_rate,
)
from services.air_freight_rate.workers.update_air_freight_rate_jobs_to_backlog import (
    update_air_freight_rate_jobs_to_backlog,
)
from services.air_freight_rate.workers.update_air_freight_rate_job_on_rate_addition import (
    update_air_freight_rate_job_on_rate_addition,
)
from celery.schedules import crontab
from services.air_freight_rate.interactions.create_air_freight_rate_job import update_live_booking_visiblity_for_air_freight_rate_job

from services.air_freight_rate.workers.update_air_freight_rate_local_jobs_to_backlog import (
    update_air_freight_rate_local_jobs_to_backlog
)
from services.air_freight_rate.interactions.create_air_freight_rate_local_job import (
    update_live_booking_visiblity_for_air_freight_rate_local_job
)
from services.air_freight_rate.workers.update_air_freight_rate_local_job_on_rate_addition import (
    update_air_freight_rate_local_job_on_rate_addition,
)

tasks = {
    'update_air_freight_jobs_status_to_backlogs': {
        'task': 'services.air_freight_rate.air_celery_worker.update_air_freight_rate_jobs_to_backlog_delay',
        'schedule': crontab(hour=22, minute=10),
        'options': {'queue': 'fcl_freight_rate'}
    },
    "update_air_freight_local_jobs_status_to_backlogs": {
        "task": "services.air_freight_rate.air_celery_worker.update_air_freight_rate_local_jobs_to_backlog_delay",
        "schedule": crontab(hour=22, minute=55),
        "options": {"queue": "fcl_freight_rate"}
    },
    # 'adjust_air_freight_dynamic_pricing':{
    #     'task': 'services.air_freight_rate.air_celery_worker..adjust_air_freight_dynamic_pricing',
    #     'schedule': crontab(minute=00,hour=00),
    #     'options': {'queue' : 'fcl_freight_rate'}
    # },
    'send_air_freight_local_charges_update_reminder_notification':{
        'task': 'services.air_freight_rate.air_celery_worker..send_air_freight_local_charges_update_reminder_notification_in_delay',
        'schedule': crontab(minute=00,hour=21,day_of_month = '1'),
        'options': {'queue': 'low'}
    },
    'send_expired_air_freight_rate_notification':{
        'task': 'services.air_freight_rate.air_celery_worker..send_expired_air_freight_rate_notification_in_delay',
        'schedule': crontab(minute=30,hour=20),
        'options': {'queue' : 'low'}
    },
    'send_near_expiry_air_freight_rate_notification':{
        'task': 'services.air_freight_rate.air_celery_worker..send_near_expiry_air_freight_rate_notification_in_delay',
        'schedule': crontab(minute=00,hour=20),
        'options': {'queue' : 'low'}
    },
    'adjust_air_freight_rate_airline_factors':{
        'task': 'services.air_freight_rate.air_celery_worker..air_freight_airline_factors_in_delay',
        'schedule': crontab(hour=5, minute=30, day_of_week='sun'),
        'options': {'queue': 'low'}
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

@celery.task(bind = True, max_retries=5, retry_backoff = True)
def adjust_air_freight_dynamic_pricing(self):
    try:
        # return True
        return invoice_rates_updation()
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, retry_backoff=True, max_retries=1)
def process_freight_look_rates(self, rate, locations):
    try:
        return create_air_freight_rate_api(rate=rate, locations=locations)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)
        
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
        
@celery.task(bind=True, max_retries=1, retry_backoff=True)
def update_live_booking_visiblity_for_air_freight_rate_local_job_delay(self, job_id):
    try:
        return update_live_booking_visiblity_for_air_freight_rate_local_job(job_id)
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)
        
@celery.task(bind=True, max_retries=1, retry_backoff=True)
def update_air_freight_rate_local_job_on_rate_addition_delay(self, request, id):
    try:
        return update_air_freight_rate_local_job_on_rate_addition(request, id)
    except Exception as exc:
        if type(exc).__name__ == "HTTPException":
            pass
        else:
            raise self.retry(exc=exc)
        
@celery.task(bind = True, max_retries=5, retry_backoff = True)
def create_air_freight_rate_delay(self, request):
    try:
        # return create_draft_air_freight_rate(request)
        return create_air_freight_rate(request)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)
    
@celery.task(bind = True, max_retries=5, retry_backoff = True)
def create_saas_air_schedule_airport_pair_delay (self,air_object,request):
    try:
        create_saas_air_schedule_airport_pair(air_object,request)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, retry_backoff = True, max_retries=5)
def create_air_freight_rate_local_delay(self, request):
    try:
        return create_air_freight_rate_local(request)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True,retry_backoff = True, max_retries=5)
def create_air_freight_rate_freight_delay(self, request):
    try:
        return create_air_freight_rate(request)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, retry_backoff = True, max_retries=5)
def create_air_freight_rate_surcharge_delay(self, request):
    try:
        return create_air_freight_rate_surcharge(request)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, retry_backoff=True,max_retries=3)
def send_air_freight_rate_task_notification_in_delay(self,task_id):
    try:
        send_air_freight_rate_task_notification(task_id)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, retry_backoff=True,max_retries=3)
def get_rate_from_cargo_ai_in_delay(self,air_freight_rate,feedback,performed_by_id):
    try:
        get_rate_from_cargo_ai(air_freight_rate,feedback,performed_by_id)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, retry_backoff=True,max_retries=3)
def send_air_freight_local_charges_update_reminder_notification_in_delay(self):
    try:
        send_air_freight_local_charges_update_reminder_notification()
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, retry_backoff=True,max_retries=3)
def send_expired_air_freight_rate_notification_in_delay(self):
    try:
        send_expired_air_freight_rate_notification()
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, retry_backoff=True,max_retries=3)
def send_near_expiry_air_freight_rate_notification_in_delay(self):
    try:
        send_near_expiry_air_freight_rate_notification()
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)
        
@celery.task(bind = True, retry_backoff=True,max_retries=5)
def update_air_freight_rate_details_delay(self, request):
    try:
        update_air_freight_rate_request(request)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, retry_backoff = True,max_retries=1)
def air_freight_rate_prediction_feedback_delay(self, result):
    try:
        create_air_freight_rate_feedback(result)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)
        
@celery.task(bind = True,retry_backoff=True,max_retries=3)
def air_freight_airline_factors_in_delay(self):
    try:
        relate_ailine = RelateAirline()
        relate_ailine.relate_airlines()
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc) 

@celery.task(bind=True, retry_backoff=True,max_retries=3)
def transform_air_dynamic_pricing(self, new_rate, affected_transformation, new):
    try:
        air_freight_vyuh = AirFreightVyuhSetter(new_rate=new_rate)
        air_freight_vyuh.adjust_price_for_tranformation(affected_transformation=affected_transformation, new=new)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, retry_backoff=True,max_retries=3)
def extend_air_freight_rates(self, rate, source = 'rate_extension'):
    try:
        air_freight_vyuh = AirFreightVyuhProducer(rate=rate)
        air_freight_vyuh.extend_rate(source=source)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)
        
@celery.task(bind = True,retry_backoff=True,max_retries=3)
def extend_air_freight_rates_in_delay(self, rate,base_to_base=False):
    try:
        air_freight_vyuh = AirFreightVyuhProducer(rate=rate)
        air_freight_vyuh.extend_rate(base_to_base)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)