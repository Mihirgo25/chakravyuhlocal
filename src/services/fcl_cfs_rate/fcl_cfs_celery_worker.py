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
def send_notifications_to_supply_agents_cfs_feedback_delay(self, object):
    try:
        object.send_notifications_to_supply_agents()
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