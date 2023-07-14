import peewee as pw
from peewee_migrate import Migrator
from services.fcl_freight_rate.models.fcl_freight_rate_feedback import FclFreightRateFeedback
from services.fcl_freight_rate.models.fcl_freight_rate_request import FclFreightRateRequest
from playhouse.postgres_ext import *

SQL = pw.SQL


def migrate(migrator: Migrator, database, fake=False, **kwargs):
    migrator.sql('ALTER TABLE rate_sheets ALTER COLUMN file_url TYPE text;')
    migrator.sql('ALTER TABLE rate_sheets ALTER COLUMN comment TYPE text;')


def rollback(migrator: Migrator, database, fake=False, **kwargs):
    pass

