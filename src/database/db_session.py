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

db_nirvana = PostgresqlDatabase(
    'cogoport_api_nirvana1',
    autorollback = True,
    user = DATABASE_USER,
    password = DATABASE_PASSWORD,
    host = DATABASE_HOST,
    port = DATABASE_PORT
    )