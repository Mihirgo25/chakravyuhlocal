import datetime as dt
import peewee as pw
from peewee_migrate import Migrator
from decimal import ROUND_HALF_EVEN
from peewee import *

from playhouse.postgres_ext import *

from services.fcl_freight_rate.models.fcl_freight_rate_audit import FclFreightRateAudit

try:
    import playhouse.postgres_ext as pw_pext
except ImportError:
    pass

SQL = pw.SQL


def migrate(migrator: Migrator, database, fake=False, **kwargs):
    """write here"""
    migrator.add_fields(FclFreightRateAudit, extended_from_object_id=UUIDField(index=True,null=True))  
    migrator.sql('Create index fcl_freight_rate_audit_source on fcl_freight_rate_audits (source) ;')
    migrator.sql('Create index fcl_freight_rate_audit_extended_from_object_id on fcl_freight_rate_audits (extended_from_object_id) ;')
def rollback(migrator: Migrator, database, fake=False, **kwargs):
    pass