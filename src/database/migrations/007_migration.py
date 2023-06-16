from peewee_migrate import Migrator
from playhouse.postgres_ext import BinaryJSONField, ArrayField
from services.haulage_freight_rate.models.haulage_freight_rate import HaulageFreightRate
from peewee import *
from playhouse.postgres_ext import *

def migrate(migrator: Migrator, database, fake=False, **kwargs):
    """Write your migrations here."""
    migrator.add_fields(HaulageFreightRate, importer_exporter = BinaryJSONField(index=True, null=True))
    migrator.add_fields(HaulageFreightRate, service_provider= BinaryJSONField(index=True, null=True))
    migrator.add_fields(HaulageFreightRate, origin_location= BinaryJSONField(index=True, null=True))
    migrator.add_fields(HaulageFreightRate, destination_location= BinaryJSONField(index=True, null=True))
    migrator.add_fields(HaulageFreightRate, shipping_line = BinaryJSONField(index=True, null=True))
    migrator.add_fields(HaulageFreightRate, validities = BinaryJSONField(index=True, null=True))

def rollback(migrator: Migrator, database, fake=False, **kwargs):
    """Write your rollback migrations here."""