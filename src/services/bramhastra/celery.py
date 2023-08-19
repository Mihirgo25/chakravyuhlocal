from celery_worker import celery
from services.bramhastra.brahmastra import Brahmastra

@celery.task(bind=True,retry_backoff=True,max_retries=5)
def brahmastra_in_delay(self):
    # using this until we get all queries right
    try:
        brahmastra=Brahmastra()
        brahmastra.used_by(arjun = True)
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
def send_rate_stats_in_delay(self,action,request,freight):
    from services.fcl_freight_rate.helpers.fcl_freight_statistics_helper import send_rate_stats
    try:
        return send_rate_stats(action,request,freight)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, retry_backoff=True,max_retries=5)
def send_feedback_delete_stats_in_delay(self,obj):
    from services.fcl_freight_rate.helpers.fcl_freight_statistics_helper import send_feedback_delete_stats
    try:
        send_feedback_delete_stats(obj)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)
     
        
@celery.task(bind = True, retry_backoff=True,max_retries=5)
def send_delete_request_stats_in_delay(self,obj):
    from services.fcl_freight_rate.helpers.fcl_freight_statistics_helper import send_request_delete_stats
    try:
        send_request_delete_stats(obj)
    except Exception as exc:
        
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)
        

@celery.task(bind = True, retry_backoff=True,max_retries=5)
def send_request_stats_in_delay(self,action,object):
    from services.fcl_freight_rate.helpers.fcl_freight_statistics_helper import send_request_stats
    try:
        send_request_stats(action,object)
    except Exception as exc:
        
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)
        
        
@celery.task(bind = True, retry_backoff=True,max_retries=5)
def send_feedback_statistics_in_delay(self,action,feedback,request = None):
    from services.fcl_freight_rate.helpers.fcl_freight_statistics_helper import send_feedback_statistics
    try:
        send_feedback_statistics(action,feedback,request)
    except Exception as exc:
        
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)