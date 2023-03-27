from peewee import *
from configs.env import *

db = PostgresqlDatabase(
    DATABASE_NAME,
    autorollback = True,
    user = DATABASE_USER,
    password = DATABASE_PASSWORD,
    host = DATABASE_HOST,
    port = DATABASE_PORT
    )

db_cogo_lens = PostgresqlDatabase(
    COGO_LENS_DATABASE_NAME,
    autorollback = True,
    user = COGO_LENS_DATABASE_USER,
    password = COGO_LENS_DATABASE_PASSWORD,
    host = COGO_LENS_DATABASE_HOST,
    port = COGO_LENS_DATABASE_PORT
    )