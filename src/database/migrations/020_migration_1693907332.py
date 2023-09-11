import peewee as pw
from peewee_migrate import Migrator
from peewee import *
from playhouse.postgres_ext import *
try:
    import playhouse.postgres_ext as pw_pext
except ImportError:
    pass
from services.fcl_freight_rate.models.fcl_freight_rate_jobs import FclFreightRateJob
from services.air_freight_rate.models.air_freight_rate_jobs import AirFreightRateJob

SQL = pw.SQL


def migrate(migrator: Migrator, database, fake=False, **kwargs):
    """Write your migrations here."""
    migrator.add_fields(FclFreightRateJob, rate_id = UUIDField(null=True, index=True))
    migrator.add_fields(AirFreightRateJob, rate_id = UUIDField(null=True, index=True))

def rollback(migrator: Migrator, database, fake=False, **kwargs):
    pass