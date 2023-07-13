import datetime as dt
import peewee as pw
from peewee_migrate import Migrator
from decimal import ROUND_HALF_EVEN
# from db_session import db
from services.fcl_customs_rate.models.fcl_customs_rate_feedback import FclCustomsRateFeedback
from peewee import *

from playhouse.postgres_ext import *

try:
    import playhouse.postgres_ext as pw_pext
except ImportError:
    pass

SQL = pw.SQL

def migrate(migrator: Migrator, database, fake=False, **kwargs):
    """Write your migrations here."""
    migrator.add_fields(FclCustomsRateFeedback, reverted_rate = BinaryJSONField(null=True))

def rollback(migrator: Migrator, database, fake=False, **kwargs):
    """Write your rollback migrations here."""