import peewee as pw
from peewee_migrate import Migrator
from peewee import *
from playhouse.postgres_ext import *
from services.rate_sheet.models.rate_sheet_audits import RateSheetAudit

try:
    import playhouse.postgres_ext as pw_pext
except ImportError:
    pass

SQL = pw.SQL


def migrate(migrator: Migrator, database, fake=False, **kwargs):
    migrator.add_fields(RateSheetAudit, performed_by_type=CharField(index=True,null=True)) 
    
def rollback(migrator: Migrator, database, fake=False, **kwargs):
    pass