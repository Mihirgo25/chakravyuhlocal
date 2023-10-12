from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from decorators import timed_cache, redis_timed_cache
import redis
from fastapi.encoders import jsonable_encoder

conn = redis.StrictRedis(
    host= 'localhost',
    port = 6378,
    db=2,
)

@timed_cache(maxsize=2)
def fn(filter):
    id = filter.get("id")
    query = (
        AirFreightRate.select()
        .where(AirFreightRate.destination_airport_id == id)
        .order_by(AirFreightRate.accuracy)
        .limit(1)
    )
    return list(query.dicts())[0]

@redis_timed_cache(maxsize=2, conn=conn)
def redis_fn(filter):
    id = filter.get("id")
    query = (
        AirFreightRate.select()
        .where(AirFreightRate.destination_airport_id == id)
        .order_by(AirFreightRate.accuracy)
        .limit(1)
    )
    return list(query.dicts())[0]
