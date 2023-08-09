from database.db_session import rd
from fastapi.responses import PlainTextResponse
from fastapi import Request
from functools import wraps
from configs.env import APP_ENV
import random


class RateLimiter:
    def add(self, time_window: int, max_requests: int):
        def decorator(func):
            @wraps(func)
            def wrap_func(request, *args, **kwargs):
                
                if APP_ENV == 'development':
                    return func(request, *args, **kwargs)

                ip_address = self.get_ip_address(request)
                key = f"{func.__name__}:{ip_address}"
                count = rd.incr(key)
 
                if count == 1:
                    dt = min(10 * time_window//100, 720)
                    random_time = random.randint(time_window - dt, time_window + dt)
                    
                    rd.expire(key, random_time)
                if count > max_requests:
                    return PlainTextResponse("Too many Requests", status_code=429)
                return func(request, *args, **kwargs)

            return wrap_func

        return decorator
    
    def get_ip_address(self,request):
        if 'user_ip_address' in request.headers:
            return request.headers['user_ip_address']
        
        if "forwarded" in request.headers:
            forwarded =  request.headers["forwarded"]
            
            try:
                forwarded = forwarded.split(';')

                for part in forwarded:
                    if part.startswith('for='):
                        return part.split('=')[1]
            except Exception:
                return forwarded

        else:
            if not request.client or not request.client.host:
                return "127.0.0.1"
            
            return request.client.host


rate_limiter = RateLimiter()
