from celery_worker import celery

@celery.task(bind = True, retry_backoff=True,max_retries=1)
def async_test(self):
    pass