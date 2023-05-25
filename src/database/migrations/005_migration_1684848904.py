from peewee import *
from peewee_migrate import Migrator
from services.fcl_freight_rate.models.fcl_freight_rate_request import FclFreightRateRequest
from playhouse.postgres_ext import ArrayField

def migrate(migrator: Migrator, database, fake=False, **kwargs):
    migrator.change_fields(FclFreightRateRequest, remarks = ArrayField(constraints=[SQL("DEFAULT '{}'::character varying[]")], field_class=TextField, null=True)) 

def rollback(migrator: Migrator, database, fake=False, **kwargs):
    pass
