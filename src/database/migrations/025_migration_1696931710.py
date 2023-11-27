import datetime as dt
import peewee as pw
from peewee_migrate import Migrator
from decimal import ROUND_HALF_EVEN
from playhouse.postgres_ext import *
from services.ftl_freight_rate.models.ftl_freight_rate import FtlFreightRate

try:
    import playhouse.postgres_ext as pw_pext
except ImportError:
    pass

SQL = pw.SQL


def migrate(migrator: Migrator, database, fake=False, **kwargs):
    migrator.add_fields(FtlFreightRate, distance = FloatField(null=True)) 
    migrator.add_fields(FtlFreightRate, origin_region_id = UUIDField(null=True, index=True))
    migrator.add_fields(FtlFreightRate, destination_region_id = UUIDField(null=True, index=True)) 


def rollback(migrator: Migrator, database, fake=False, **kwargs):
    pass