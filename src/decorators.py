import json
import time
import uuid
import random
from functools import wraps
from fastapi.encoders import jsonable_encoder
from configs.global_constants import REFRESH_TIME
from database.db_session import rd
from configs.env import APP_ENV
import json
from enums.global_enums import AppEnv


def cached(maxsize=2):
    def decorator(func):
        cache_sorted_keys = f"timed_cache:sorted_set:{func.__name__}"
        cache = f"timed_cache:hash:{func.__name__}"

        def clean():
            rand = [1, 0][random.random() > 0.6]
            if rand:
                all_keys = rd.zrange(cache_sorted_keys, 0, -1)
                for key in all_keys:
                    if not rd.exists(key):
                        rd.zrem(cache_sorted_keys, key)
                        rd.hdel(cache, key)

        clean()

        @wraps(func)
        def wrapper(*args, **kwargs):
            key_args = tuple(
                str(arg)
                if isinstance(arg, uuid.UUID)
                else json.dumps(arg)
                if APP_ENV == AppEnv.production
                else arg
                for arg in args[1:]
            )
            key_kwargs = {
                k: str(v) if isinstance(v, uuid.UUID) else v for k, v in kwargs.items()
            }
            key = (key_args, frozenset(key_kwargs.items()))
            cached_result = rd.hget(cache, "timed_cache:" + str(key))
            if cached_result:
                cached_data = json.loads(cached_result)
                result, process_time = (
                    cached_data["result"],
                    cached_data["process_time"],
                )
                return add_to_cache(key, result, process_time)
            else:
                start_time = time.time()
                result = func(*args, **kwargs)
                process_time = time.time() - start_time
                return add_to_cache(key, result, process_time)

        def add_to_cache(key, result, process_time):
            if not isinstance(result, dict) or not result:
                return result
            if rd.zcard(cache_sorted_keys) == maxsize:
                least_score_tuple = rd.zrange(cache_sorted_keys, 0, 0, withscores=True)[
                    0
                ]
                if process_time > least_score_tuple[1]:
                    remove_from_cache(str(least_score_tuple[0]))
                else:
                    return result
            cached_data = {
                "result": jsonable_encoder(result),
                "process_time": process_time,
            }
            rd.zadd(
                cache_sorted_keys,
                {"timed_cache:" + str(key): float(process_time)},
            )
            rd.hset(cache, "timed_cache:" + str(key), json.dumps(cached_data))
            rd.setex("timed_cache:" + str(key), REFRESH_TIME, f"{process_time}")
            return result

        def remove_from_cache(key):
            rd.zrem(cache_sorted_keys, key)
            rd.hdel(cache, key)
            rd.delete(key)

        return wrapper

    return decorator


def clean_cached():
    for key in rd.keys("timed_cache:*"):
        rd.delete(key)
