import peewee as pw
from peewee_migrate import Migrator
from peewee import *
from playhouse.postgres_ext import *
try:
    import playhouse.postgres_ext as pw_pext
except ImportError:
    pass
from services.air_freight_rate.models.air_freight_rate_jobs import AirFreightRateJob
from services.air_customs_rate.models.air_customs_rate_jobs import AirCustomsRateJob
from services.fcl_freight_rate.models.fcl_freight_rate_jobs import FclFreightRateJob
from services.fcl_customs_rate.models.fcl_customs_rate_jobs import FclCustomsRateJob
from services.haulage_freight_rate.models.haulage_freight_rate_jobs import HaulageFreightRateJob
from services.ltl_freight_rate.models.ltl_freight_rate_jobs import LtlFreightRateJob
from services.ftl_freight_rate.models.ftl_freight_rate_jobs import FtlFreightRateJob
from services.fcl_cfs_rate.models.fcl_cfs_rate_jobs import FclCfsRateJob

SQL = pw.SQL


def migrate(migrator: Migrator, database, fake=False, **kwargs):
    """Write your migrations here."""
    migrator.add_fields(AirFreightRateJob, is_visible = BooleanField(default=True))
    migrator.add_fields(FclFreightRateJob, is_visible = BooleanField(default=True))
    migrator.add_fields(AirCustomsRateJob, is_visible = BooleanField(default=True))
    migrator.add_fields(FclCustomsRateJob, is_visible = BooleanField(default=True))
    migrator.add_fields(HaulageFreightRateJob, is_visible = BooleanField(default=True))
    migrator.add_fields(LtlFreightRateJob, is_visible = BooleanField(default=True))
    migrator.add_fields(FtlFreightRateJob, is_visible = BooleanField(default=True))
    migrator.add_fields(FclCfsRateJob, is_visible = BooleanField(default=True))


    
def rollback(migrator: Migrator, database, fake=False, **kwargs):
    pass