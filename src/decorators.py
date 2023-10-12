import json
import time
import redis
import uuid
from functools import wraps
from fastapi.encoders import jsonable_encoder

def redis_timed_cache(maxsize=500, conn=None):
    def decorator(func):
        cache_sorted_keys = f"timed_cache:sorted_set:{func.__name__}"
        cache = f"timed_cache:hash:{func.__name__}"

        @wraps(func)
        def wrapper(*args, **kwargs):
            key_args = tuple(str(arg) if isinstance(arg, uuid.UUID) else arg for arg in args)
            key_kwargs = {k: str(v) if isinstance(v, uuid.UUID) else v for k, v in kwargs.items()}
            key = (key_args, frozenset(key_kwargs.items()))
            cached_result = conn.hget(cache, str(key))
            if cached_result:
                cached_data = json.loads(cached_result.decode('utf-8'))
                result, process_time = cached_data['result'], cached_data['process_time']
                
            else:
                start_time = time.time()
                result = func(*args, **kwargs)
                process_time = time.time() - start_time

                cached_data = {'result': jsonable_encoder(result), 'process_time': process_time}
                conn.zadd(cache_sorted_keys, {str(key): process_time})
                conn.hset(cache, str(key), json.dumps(cached_data))

                if conn.zcard(cache_sorted_keys) > maxsize:
                    least_processing_time_key = conn.zrange(cache_sorted_keys, 0, 0, withscores=True)[0][0]
                    conn.zrem(cache_sorted_keys, least_processing_time_key)
                    conn.hdel(cache, least_processing_time_key.decode('utf-8'))

            return result, process_time

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


class Node:
    def __init__(self, key, value, process_time):
        self.key = key
        self.value = value
        self.process_time = process_time
        self.prev = None
        self.next = None

def timed_cache(maxsize = 500):
    head = Node(None, None, None)
    tail = Node(None, None, None)
    head.next = tail
    tail.prev = head

    def _insert_after(prev_node, key, value, process_time):
        new_node = Node(key, value, process_time)
        new_node.prev = prev_node
        new_node.next = prev_node.next
        prev_node.next.prev = new_node
        prev_node.next = new_node

    def decorator(func):

        cache = {}

        @wraps(func)
        def wrapper(*args, **kwargs):
            k = args, tuple(kwargs.items())
            key = f"{func.__name__}"+str(json.dumps(k[0]))
            print(key)
            if key in cache:
                node = cache[key]
                result, process_time = node.value, node.process_time
            else:
                start_time = time.time()
                result = func(*args, **kwargs)
                process_time = time.time() - start_time
                if len(cache) == maxsize:
                    if process_time > tail.prev.process_time:
                        current_node = head.next
                        while current_node != tail and current_node.process_time > process_time:
                            current_node = current_node.next
                        _insert_after(current_node.prev, key, result, process_time)
                        del cache[tail.prev.key]
                        tail.prev.prev.next = tail
                        tail.prev = tail.prev.prev

                    else:
                        return result, process_time
                    
                elif len(cache) < maxsize:
                    current_node = head.next
                    while current_node != tail and current_node.process_time > process_time:
                        current_node = current_node.next
                    _insert_after(current_node.prev, key, result, process_time)
                
                cache[key] = Node(key, result, process_time)
                
            return result, process_time

        def clear():
            cache = {}

        wrapper.clear = clear       
        return wrapper

    return decorator






