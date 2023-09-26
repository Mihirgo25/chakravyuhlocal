from celery_worker import celery
from services.air_customs_rate.helpers.update_organization_air_customs import update_organization_air_customs
from services.air_customs_rate.interaction.create_air_customs_rate import create_air_customs_rate

@celery.task(bind = True, retry_backoff=True, max_retries=5)
def air_customs_functions_delay(self,air_customs_object,request):
    try:
        update_organization_air_customs(request)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, retry_backoff = True, max_retries=5)
def bulk_operation_perform_action_functions_air_customs_delay(self, action_name, object):
    try:
        eval(f"object.perform_{action_name}_action()")
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, retry_backoff=True, max_retries=5)
def create_air_customs_rate_delay(self, request):
    try:
        return create_air_customs_rate(request)
    except Exception as e:
        if type(e).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= e)
        
@celery.task(bind = True, retry_backoff=True, max_retries=5)
def send_closed_notifications_to_sales_agent_air_customs_delay(self, object):
    try:
        object.send_closed_notifications_to_sales_agent()
    except Exception as e:
        if type(e).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= e)