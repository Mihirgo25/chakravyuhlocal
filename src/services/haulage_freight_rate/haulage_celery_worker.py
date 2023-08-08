from celery_worker import celery
from services.haulage_freight_rate.helpers.haulage_freight_rate_helpers import adding_multiple_service_object
from services.haulage_freight_rate.interactions.update_haulage_freight_rate_request import update_haulage_freight_rate_request
from services.haulage_freight_rate.interactions.create_haulage_freight_rate import create_haulage_freight_rate


@celery.task(bind = True, max_retries=3, retry_backoff = True)    
def bulk_operation_perform_action_functions_haulage(self, action_name,object,sourced_by_id,procured_by_id):
    try:
        eval(f"object.perform_{action_name}_action(sourced_by_id='{sourced_by_id}',procured_by_id='{procured_by_id}')")
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)
        
@celery.task(bind = True, max_retries=3, retry_backoff = True)
def update_haulage_freight_rate_request_delay(self, request):
    try:
        update_haulage_freight_rate_request(request)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)
        

@celery.task(bind = True, max_retries=3, retry_backoff = True)
def delay_haulage_functions(self,haulage_object,request):
    try:
       adding_multiple_service_object(haulage_object, request)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)


@celery.task(bind = True, max_retries=3, retry_backoff=True)
def create_haulage_freight_rate_delay(self, request):
    try:
        return create_haulage_freight_rate(request)
    except Exception as e:
        if type(e).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= e)

