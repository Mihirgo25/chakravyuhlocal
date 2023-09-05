import peewee as pw
from peewee_migrate import Migrator
from peewee import *
from playhouse.postgres_ext import *
try:
    import playhouse.postgres_ext as pw_pext
except ImportError:
    pass
from services.bramhastra.models.fcl_freight_rate_statistic import FclFreightRateStatistic

SQL = pw.SQL


def migrate(migrator: Migrator, database, fake=False, **kwargs):
    """Write your migrations here."""
    migrator.add_fields(FclFreightRateStatistic, bas_price = FloatField(default = 0,null = True))
    migrator.add_fields(FclFreightRateStatistic, bas_standard_price = FloatField(default = 0,null = True))
    migrator.add_fields(FclFreightRateStatistic, bas_currency = CharField(max_length = 3,null = True))


def rollback(migrator: Migrator, database, fake=False, **kwargs):
    pass