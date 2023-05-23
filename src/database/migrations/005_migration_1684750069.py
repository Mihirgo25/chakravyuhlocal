from peewee import *
from peewee_migrate import Migrator
from services.fcl_freight_rate.models.fcl_freight_rate_request import FclFreightRateRequest
from playhouse.postgres_ext import ArrayField

def migrate(migrator: Migrator, database, fake=False, **kwargs):
    migrator.add_fields(FclFreightRateRequest, reverted_by_user_ids=ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, null=True))
    migrator.add_fields(FclFreightRateRequest, reverted_rates_count=IntegerField(null=True, default=0))
    migrator.add_fields(FclFreightRateRequest, expiration_time=DateTimeField(null=True))

def rollback(migrator: Migrator, database, fake=False, **kwargs):
    pass

