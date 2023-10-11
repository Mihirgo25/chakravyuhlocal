import datetime as dt
import peewee as pw
from peewee_migrate import Migrator
from decimal import ROUND_HALF_EVEN
from playhouse.postgres_ext import *
from services.fcl_freight_rate.models.fcl_freight_rate_local import FclFreightRateLocal

try:
    import playhouse.postgres_ext as pw_pext
except ImportError:
    pass

SQL = pw.SQL


def migrate(migrator: Migrator, database, fake=False, **kwargs):
    migrator.add_fields(FclFreightRateLocal, terminal_id = UUIDField(index=True,null=True)) 
    migrator.add_fields(FclFreightRateLocal, terminal = BinaryJSONField(null=True)) 


def rollback(migrator: Migrator, database, fake=False, **kwargs):
    pass