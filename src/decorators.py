import json
import time
import redis
import uuid
from functools import wraps
from fastapi.encoders import jsonable_encoder
from configs.global_constants import REFRESH_TIME

def redis_timed_cache(maxsize=500, conn=None):
    def decorator(func):
        cache_sorted_keys = f"timed_cache:sorted_set:{func.__name__}"
        cache = f"timed_cache:hash:{func.__name__}"

        def cleanup_expired_keys():
            all_keys = conn.zrange(cache_sorted_keys, 0, -1)
            for key in all_keys:
                if not conn.exists(key):
                    conn.zrem(cache_sorted_keys, key)
                    conn.hdel(cache, key)
        
        def add_to_cache(key, cached_data):
            hits, process_time = cached_data['hits'], cached_data['processe_time']
            conn.zadd(cache_sorted_keys, {str(key): hits * float(process_time)})
            conn.hset(cache, str(key), json.dumps(cached_data))
            conn.setex(str(key), REFRESH_TIME,f"{hits},{process_time}")
        
        def remove_from_cache(key):
            conn.zrem(cache_sorted_keys, key)
            conn.hdel(cache, key)
            conn.delete(key)


        @wraps(func)
        def wrapper(*args, **kwargs):
            key_args = tuple(str(arg) if isinstance(arg, uuid.UUID) else arg for arg in args)
            key_kwargs = {k: str(v) if isinstance(v, uuid.UUID) else v for k, v in kwargs.items()}
            key = (key_args, frozenset(key_kwargs.items()))
            cleanup_expired_keys()
            cached_result = conn.hget(cache, str(key))
            if cached_result:
                cached_data = json.loads(cached_result)
                result, hits, process_time = cached_data['result'], int(cached_data['hits']), cached_data['process_time']
                hits += 1
                cached_data = {'result': jsonable_encoder(result), 'hits': hits, 'process_time': process_time}
                add_to_cache(key, cached_data)

            else:
                start_time = time.time()
                result = func(*args, **kwargs)
                process_time = time.time() - start_time
                hits = 1
                cached_data = {'result': jsonable_encoder(result), 'hits': hits, 'process_time': process_time}
                add_to_cache(key, cached_data)

                if conn.zcard(cache_sorted_keys) > maxsize:
                    least_processing_time_key = conn.zrange(cache_sorted_keys, 0, 0, withscores=True)[0][0]
                    remove_from_cache(least_processing_time_key)
            
            conn.expire(str(key), REFRESH_TIME)
            return result

        def cache_clear():
            conn.delete(cache)
            conn.delete(cache_sorted_keys)
        
        def init(redis_conn):
            nonlocal conn
            conn = redis_conn

        if conn:
            init(conn)

        wrapper.init = init
        wrapper.cache_clear = cache_clear
        return wrapper

    return decorator
