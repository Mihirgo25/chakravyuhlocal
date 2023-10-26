

import datetime as dt
import peewee as pw
from peewee import *
from peewee_migrate import Migrator
from decimal import ROUND_HALF_EVEN
from services.fcl_customs_rate.models.fcl_customs_rate import FclCustomsRate

try:
    import playhouse.postgres_ext as pw_pext
except ImportError:
    pass

SQL = pw.SQL


def migrate(migrator: Migrator, database, fake=False, **kwargs):
    """Write your migrations here."""
    migrator.add_fields(FclCustomsRate, cargo_handling_type = CharField(null=True, index=True))



def rollback(migrator: Migrator, database, fake=False, **kwargs):
    """Write your rollback migrations here."""

