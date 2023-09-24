import peewee
from configs.env import (
    DATABASE_NAME,
    DATABASE_PORT,
    DATABASE_USER,
    DATABASE_PASSWORD,
    DATABASE_HOST,
    REDIS_HOST,
    REDIS_PASSWORD,
    REDIS_PORT,
    REDIS_USERNAME,
    APP_ENV,
    ENVIRONMENT_TYPE
)
from playhouse.pool import PooledPostgresqlExtDatabase
import redis
from contextvars import ContextVar
import time
from functools import wraps
import logging
from playhouse.pool import PooledPostgresqlExtDatabase

logger = logging.getLogger("peewee")
db_state_default = {"closed": None, "conn": None, "ctx": None, "transactions": None}
db_state = ContextVar("db_state", default=db_state_default.copy())


class PeeweeConnectionState(peewee._ConnectionState):
    def __init__(self, **kwargs):
        super().__setattr__("_state", db_state)
        super().__init__(**kwargs)

    def __setattr__(self, name, value):
        self._state.get()[name] = value

    def __getattr__(self, name):
        return self._state.get()[name]


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter_ns()
        ret = func(*args, **kwargs)
        end_time = time.perf_counter_ns()
        elapsed_time_ms = (end_time - start_time) / 1e6
        logger.info("Execution Time: %.2f ms" % elapsed_time_ms)
        return ret

    return wrapper


db_params = {
    "database": DATABASE_NAME,
    "user": DATABASE_USER,
    "password": DATABASE_PASSWORD,
    "host": DATABASE_HOST,
    "port": DATABASE_PORT,
    "autorollback": True,
    "max_connections": 200,
}


class CustomDatabase(PooledPostgresqlExtDatabase):
    @timer
    def execute_sql(self, sql, params=None, commit=object()):
        return super().execute_sql(sql, params, commit)


db = (
    CustomDatabase(**db_params)
    if ENVIRONMENT_TYPE == "cli"
    else PooledPostgresqlExtDatabase(**db_params)
)

db._state = PeeweeConnectionState()

if APP_ENV != "development":
    rd = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=0,
        username=REDIS_USERNAME,
        password=REDIS_PASSWORD,
        ssl=True,
        ssl_cert_reqs=None,
        decode_responses=True,
    )
else:
    rd = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
