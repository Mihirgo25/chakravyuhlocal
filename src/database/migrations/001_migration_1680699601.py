import datetime as dt
import peewee as pw
from peewee_migrate import Migrator
from decimal import ROUND_HALF_EVEN
# from db_session import db
from services.fcl_freight_rate.models.fcl_freight_rate_feedback import FclFreightRateFeedback
from peewee import *

from playhouse.postgres_ext import *

try:
    import playhouse.postgres_ext as pw_pext
except ImportError:
    pass

SQL = pw.SQL


def migrate(migrator: Migrator, database, fake=False, **kwargs):
    """Write your migrations here."""
    # migrator.add_fields(FclFreightRateFeedback, origin_continent_id=UUIDField(null=True))
    # migrator.add_fields(FclFreightRateFeedback, origin_trade_id=UUIDField(null=True))
    # migrator.add_fields(FclFreightRateFeedback, origin_country_id=UUIDField(null=True))
    # migrator.add_fields(FclFreightRateFeedback, destination_port_id=UUIDField(null=True))
    # migrator.add_fields(FclFreightRateFeedback, destination_continent_id=UUIDField(null=True))
    # migrator.add_fields(FclFreightRateFeedback, destination_trade_id=UUIDField(null=True))
    # migrator.add_fields(FclFreightRateFeedback, destination_country_id=UUIDField(null=True))
    # migrator.add_fields(FclFreightRateFeedback, commodity=CharField(null=True))
    # migrator.add_fields(FclFreightRateFeedback, container_size=CharField(null=True))
    # migrator.add_fields(FclFreightRateFeedback, container_type=CharField(null=True))
    # migrator.add_fields(FclFreightRateFeedback, service_provider_id=UUIDField(null=True))
    # migrator.add_fields(FclFreightRateFeedback, origin_port=BinaryJSONField(null=True))
    # migrator.add_fields(FclFreightRateFeedback, destination_port=BinaryJSONField(null=True))




def rollback(migrator: Migrator, database, fake=False, **kwargs):
    """Write your rollback migrations here."""

