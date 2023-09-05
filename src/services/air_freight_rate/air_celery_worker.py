from celery_worker import celery
from services.air_freight_rate.workers.air_freight_cancelled_shipments_scheduler import air_freight_cancelled_shipments_scheduler
from services.air_freight_rate.workers.air_freight_critical_port_pairs_scheduler import air_freight_critical_port_pairs_scheduler
from services.air_freight_rate.workers.air_freight_expiring_rates_scheduler import air_freight_expiring_rates_scheduler
from services.air_freight_rate.workers.air_freight_spot_search_predicted_rates_scheduler import air_freight_spot_predicted_rates_search_scheduler


@celery.task(bind = True, retry_backoff=True, max_retries=3)
def air_freight_cancelled_shipments_in_delay(self):
    try:
        air_freight_cancelled_shipments_scheduler()
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)
        
@celery.task(bind=True, max_retries=3, retry_backoff = True)
def air_freight_critical_port_pairs_delay(self):
    try:
        air_freight_critical_port_pairs_scheduler()
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)
        
@celery.task(bind = True, retry_backoff=True, max_retries=3)
def air_freight_expiring_rates_in_delay(self):
    try:
        air_freight_expiring_rates_scheduler()
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, max_retries=5, retry_backoff = True)
def air_freight_spot_search_predicted_rates_scheduler_delay(self, is_predicted, requirements):
    try:
        return air_freight_spot_predicted_rates_search_scheduler(is_predicted, requirements)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)