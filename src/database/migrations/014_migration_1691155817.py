import peewee as pw
from peewee_migrate import Migrator
from peewee import *
from playhouse.postgres_ext import *
from services.fcl_freight_rate.models.fcl_freight_rate_audit import FclFreightRateAudit
from services.air_freight_rate.models.air_freight_rate_audit import AirFreightRateAudit
from services.fcl_customs_rate.models.fcl_customs_rate_audit import FclCustomsRateAudit

try:
    import playhouse.postgres_ext as pw_pext
except ImportError:
    pass

SQL = pw.SQL


def migrate(migrator: Migrator, database, fake=False, **kwargs):
    migrator.add_fields(FclFreightRateAudit, performed_by_type=CharField(index=True,null=True)) 
    migrator.add_fields(AirFreightRateAudit, performed_by_type=CharField(index=True,null=True))
    migrator.add_fields(FclCustomsRateAudit, performed_by_type=CharField(index=True,null=True))
    
def rollback(migrator: Migrator, database, fake=False, **kwargs):
    pass