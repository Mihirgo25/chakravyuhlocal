
from peewee import *
import peewee as pw
from peewee_migrate import Migrator
from decimal import ROUND_HALF_EVEN
from services.fcl_freight_rate.models.fcl_freight_rate_local import FclFreightRateLocal
from services.fcl_freight_rate.models.fcl_freight_rate_feedback import FclFreightRateFeedback

try:
    import playhouse.postgres_ext as pw_pext
except ImportError:
    pass

SQL = pw.SQL


def migrate(migrator: Migrator, database, fake=False, **kwargs):
    migrator.add_fields(FclFreightRateLocal, rate_type = CharField(null=False, default="market_place", index=True))
    migrator.add_fields(FclFreightRateFeedback, rate_type = CharField(null=True, index=True))



def rollback(migrator: Migrator, database, fake=False, **kwargs):
    """Write your rollback migrations here."""

