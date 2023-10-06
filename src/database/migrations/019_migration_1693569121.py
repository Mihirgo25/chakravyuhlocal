import datetime as dt
import peewee as pw
from peewee_migrate import Migrator
from decimal import ROUND_HALF_EVEN
from services.air_freight_rate.models.air_freight_rate_local import AirFreightRateLocal
from services.air_freight_rate.models.air_freight_rate_surcharge import AirFreightRateSurcharge
from peewee import *
from playhouse.postgres_ext import BinaryJSONField

try:
    import playhouse.postgres_ext as pw_pext
except ImportError:
    pass

SQL = pw.SQL


def migrate(migrator: Migrator, database, fake=False, **kwargs):
    """Write your migrations here."""
    migrator.add_fields(AirFreightRateLocal, importer_exporter_id = UUIDField(null=True))
    migrator.add_fields(AirFreightRateLocal, importer_exporter = BinaryJSONField(null=True))
    migrator.add_fields(AirFreightRateSurcharge, importer_exporter_id = UUIDField(null=True))
    migrator.add_fields(AirFreightRateSurcharge, importer_exporter = BinaryJSONField(null=True))


def rollback(migrator: Migrator, database, fake=False, **kwargs):
    """Write your rollback migrations here."""

