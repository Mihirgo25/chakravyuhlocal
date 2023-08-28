import datetime as dt
from peewee import *
from peewee_migrate import Migrator
from decimal import ROUND_HALF_EVEN
from services.fcl_customs_rate.models.fcl_customs_rate_feedback import FclCustomsRateFeedback

try:
    import playhouse.postgres_ext as pw_pext
except ImportError:
    pass

SQL = pw.SQL


def migrate(migrator: Migrator, database, fake=False, **kwargs):
    migrator.add_fields(FclCustomsRateFeedback, cargo_handling_type = CharField(null=True))


def rollback(migrator: Migrator, database, fake=False, **kwargs):
    """Write your rollback migrations here."""

