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

rd = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, username=REDIS_USERNAME, password=REDIS_PASSWORD, ssl=True, ssl_cert_reqs=None, decode_responses= True)


# print(rd, rd.keys())

db_cogo_lens = PostgresqlDatabase(
    COGO_LENS_DATABASE_NAME,
    autorollback = True,
    user = COGO_LENS_DATABASE_USER,
    password = COGO_LENS_DATABASE_PASSWORD,
    host = COGO_LENS_DATABASE_HOST,
    port = COGO_LENS_DATABASE_PORT
    )