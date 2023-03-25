from peewee import *
from configs.env import *
import redis

db = PostgresqlDatabase(
    DATABASE_NAME,
    autorollback = True,
    user = DATABASE_USER,
    password = DATABASE_PASSWORD,
    host = DATABASE_HOST,
    port = DATABASE_PORT
    )

rd = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

