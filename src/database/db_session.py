from peewee import *
from configs.env import *
import redis

db = PostgresqlDatabase(
    DATABASE_NAME,
    autorollback=True,
    user=DATABASE_USER,
    password=DATABASE_PASSWORD,
    host=DATABASE_HOST,
    port=DATABASE_PORT,
)

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
    rd = redis.Redis(host="127.0.0.1", port=6379, db=0, decode_responses=True)
    # rails_redis = None
