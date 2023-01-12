from peewee import *

db = PostgresqlDatabase(
    "cogoport_api_nirvana1",
    autorollback = True,
    user = "nirvana1",
    password = "8133d5d1",
    host = "login-nirvana1.dev.cogoport.io",
    port = "6432"
    )