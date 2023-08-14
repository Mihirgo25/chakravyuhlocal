import peewee
from configs.env import *
from playhouse.pool import PooledPostgresqlExtDatabase
import redis
from contextvars import ContextVar

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

db = PooledPostgresqlExtDatabase(
    DATABASE_NAME,
    user=DATABASE_USER,
    password=DATABASE_PASSWORD,
    host=DATABASE_HOST,
    port=DATABASE_PORT,
    autorollback=True,
    max_connections=200,
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

    # rails_redis = redis.Redis(
    #     host=RAILS_REDIS_HOST,
    #     port=RAILS_REDIS_PORT,
    #     db=0,
    #     username=RAILS_REDIS_USERNAME,
    #     password=RAILS_REDIS_PASSWORD,
    #     ssl=True,
    #     ssl_cert_reqs=None,
    #     decode_responses=True,
    # )
else:
    rd = redis.Redis(host=REDIS_HOST, port= REDIS_PORT, password=REDIS_PASSWORD,db=0, decode_responses=True)
    # rails_redis = None
