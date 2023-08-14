from celery_worker import celery
from services.bramhastra.brahmastra import Brahmastra
from services.bramhastra.interactions.apply_fcl_freight_rate_statistic import apply_fcl_freight_rate_statistic
from services.bramhastra.interactions.apply_fcl_freight_rate_feedback import apply_feedback_fcl_freight_rate_statistic
from services.bramhastra.interactions.apply_fcl_freight_rate_request_statistic import apply_fcl_freight_rate_request_statistic

@celery.task(bind=True,retry_backoff=True,max_retries=5)
def arjun_in_delay(self):
    # using this until we get all queries right
    try:
        brahmastra=Brahmastra()
        brahmastra.use(arjun = True)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)
        
@celery.task(bind=True,retry_backoff=True,max_retries=5)
def cache_data_worker_in_delay(self):
    try:
        # this caches statistics csv into redis for huge data
        from services.bramhastra.workers.cache_data_worker import FclCacheData
        FclCacheData().set_all_time_accuracy_chart()
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)
        
        
@celery.task(bind=True,retry_backoff=True,max_retries=5)
def fcl_extended_object_worker_in_delay(self):
    try:
        # this sets parent_rate_id for rates created via extensions
        from services.bramhastra.workers.fcl_extended_object_worker import FclExtendObjectWorker
        FclExtendObjectWorker().execute()
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)
        
@celery.task(bind = True, retry_backoff=True,max_retries=5)
def apply_fcl_freight_rate_statistic_delay(self,action,params):
    from services.bramhastra.request_params import ApplyFclFreightRateStatistic
    try:
        return apply_fcl_freight_rate_statistic(ApplyFclFreightRateStatistic(action = action,params = params))
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, retry_backoff=True,max_retries=5)
def apply_feedback_fcl_freight_rate_statistic_delay(self,action,params):
    from services.bramhastra.request_params import ApplyFeedbackFclFreightRateStatistics
    try:
        return apply_feedback_fcl_freight_rate_statistic(ApplyFeedbackFclFreightRateStatistics(action = action,params = params))
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)
     
        
@celery.task(bind = True, retry_backoff=True,max_retries=5)
def apply_fcl_freight_rate_request_statistic_delay(self,action,params):
    from services.bramhastra.request_params import ApplyFclFreightRateRequestStatistic
    try:
        return apply_fcl_freight_rate_request_statistic(ApplyFclFreightRateRequestStatistic(action = action,params = params))
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)