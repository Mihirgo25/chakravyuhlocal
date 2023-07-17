import peewee as pw
from peewee_migrate import Migrator
from services.fcl_freight_rate.models.fcl_freight_rate_feedback import FclFreightRateFeedback
from services.fcl_freight_rate.models.fcl_freight_rate_request import FclFreightRateRequest
from playhouse.postgres_ext import *

SQL = pw.SQL


def migrate(migrator: Migrator, database, fake=False, **kwargs):
    migrator.sql('ALTER TABLE fuel_data ALTER COLUMN fuel_price TYPE NUMERIC(20,10);')


def rollback(migrator: Migrator, database, fake=False, **kwargs):
    pass

