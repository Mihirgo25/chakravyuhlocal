from celery_worker import celery
from services.ftl_freight_rate.helpers.ftl_freight_rate_helpers import adding_multiple_service_object

@celery.task(bind = True, max_retries=5, retry_backoff = True)
def ftl_bulk_operation_perform_action_functions(self, action_name,object,sourced_by_id,procured_by_id):
    try:
        eval(f"object.perform_{action_name}_action(sourced_by_id='{sourced_by_id}',procured_by_id='{procured_by_id}')")
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, max_retries=3, retry_backoff = True)
def create_ftl_freight_rate_delay(self, request):
    from services.ftl_freight_rate.interactions.create_ftl_freight_rate import create_ftl_freight_rate
    try:
        print('function_called')
        return create_ftl_freight_rate(request)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, max_retries=5, retry_backoff = True)
def delay_ftl_functions(self,ftl_object,request):
    from services.ftl_freight_rate.models.ftl_freight_rate import FtlFreightRate
    try:
       adding_multiple_service_object(ftl_object, request)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, max_retries=5, retry_backoff = True)
def update_ftl_freight_rate_request_delay(self, request):
    from services.ftl_freight_rate.interactions.update_ftl_freight_rate_request import update_ftl_freight_rate_request
    try:
        update_ftl_freight_rate_request(request)
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, max_retries=1, retry_backoff = True)
def send_missing_or_dislike_rate_notifications_to_kam(self, object, request):
    try:
        object.send_missing_or_dislike_rate_notifications_to_kam(request.get('query_raised_by_id'), request.get('is_rate_missing_or_dislike'))
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)

@celery.task(bind = True, max_retries=1, retry_backoff = True)
def send_missing_or_dislike_rate_notifications_to_platform(self, object, request):
    try:
        object.send_missing_or_dislike_rate_notifications_to_platform(request.get('query_raised_by_id'), request.get('is_rate_missing_or_dislike'))
    except Exception as exc:
        if type(exc).__name__ == 'HTTPException':
            pass
        else:
            raise self.retry(exc= exc)