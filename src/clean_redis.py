from database.db_session import rd
from services.chakravyuh.models.fcl_freight_rate_estimation import FclFreightRateEstimation
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from fastapi.encoders import jsonable_encoder
from micro_services.client import maps
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
        delay_func(object)
    print('Done')


def update_transformation_objects():
    origins = FclFreightRateEstimation.select(FclFreightRateEstimation.origin_location_id.distinct()).where(FclFreightRateEstimation.origin_location.is_null(True), FclFreightRateEstimation.status == 'active')
    destinatons = FclFreightRateEstimation.select(FclFreightRateEstimation.destination_location_id.distinct()).where(FclFreightRateEstimation.destination_location.is_null(True), FclFreightRateEstimation.status == 'active')
    limit_size = 50
    origin_count = 0
    while True:
        rates = origins.limit(limit_size)
        if not rates.exists():
            break

        estimations = jsonable_encoder(list(rates.dicts()))
        location_ids = []

        for estimation in estimations:
            location_ids.append(estimation['origin_location_id'])
        
        locations_list = maps.list_locations({ 'filters': { 'id': location_ids }, 'page_limit': 50 })

        if 'list' in locations_list:
            locations = locations_list['list']
            for location in locations:
                FclFreightRateEstimation.update(origin_location=location).where(
                    FclFreightRateEstimation.origin_location_id == location['id']
                ).execute()
        
        origin_count = origin_count + 1
        print('O', origin_count)
    
    destination_count = 0
    while True:
        rates = destinatons.limit(limit_size)
        if not rates.exists():
            break

        estimations = jsonable_encoder(list(rates.dicts()))
        location_ids = []

        for estimation in estimations:
            location_ids.append(estimation['destination_location_id'])
        
        locations_list = maps.list_locations({ 'filters': { 'id': location_ids }, 'page_limit': 50 })

        print(location_ids)

        if 'list' in locations_list:
            locations = locations_list['list']
            for location in locations:
                FclFreightRateEstimation.update(destination_location=location).where(
                    FclFreightRateEstimation.destination_location_id == location['id']
                ).execute()
        
        destination_count = destination_count + 1
        print('D', destination_count)


    print('Done')
    
    
def delay_func(object):
    get_multiple_service_objects(object)
    
    
