from peewee import *
from peewee_migrate import Migrator
from services.haulage_freight_rate.models.wagon_types import WagonTypes
from playhouse.postgres_ext import ArrayField

def migrate(migrator: Migrator, database, fake=False, **kwargs):
    migrator.sql('ALTER TABLE wagon_types DROP COLUMN wagon_type_id;')
    migrator.add_fields(WagonTypes, wagon_type=CharField(null=True))

def rollback(migrator: Migrator, database, fake=False, **kwargs):
    pass

