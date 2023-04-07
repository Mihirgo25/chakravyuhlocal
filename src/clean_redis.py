from database.db_session import rd
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.helpers.get_multiple_service_objects import get_multiple_service_objects

def clean_full_redis():
    redis_keys = rd.keys('*celery-task-meta*')
    print('Total Keys', len(redis_keys))
    total_non_celery = 0
    for key in redis_keys:
        if not 'celery-task-meta' in key:
            total_non_celery = total_non_celery + 1
    if total_non_celery > 0:
        print('Including non celery keys can not delete')
    else:
        if len(redis_keys) > 0:
            rd.delete(*redis_keys)
            print('Deleted ->', total_non_celery)
        else:
            print('No Delete performed')
            
def fcl_freight_objects_updation():
    rates_to_update = FclFreightRate.select().where(
        FclFreightRate.shipping_line.is_null(True) |
        FclFreightRate.service_provider.is_null(True) |
        FclFreightRate.sourced_by.is_null(True) |
        FclFreightRate.procured_by.is_null(True)
    )

    for object in rates_to_update.iterator():
        print('Yes')
        delay_func(object)
    print('Done')
    
    
def delay_func(object):
    get_multiple_service_objects(object)
    
    
