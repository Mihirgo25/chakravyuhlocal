import peewee as pw
from peewee_migrate import Migrator
from services.fcl_freight_rate.models.fcl_freight_rate_feedback import FclFreightRateFeedback
from services.fcl_freight_rate.models.fcl_freight_rate_request import FclFreightRateRequest
from playhouse.postgres_ext import *

SQL = pw.SQL


def migrate(migrator: Migrator, database, fake=False, **kwargs):
    migrator.add_fields(FclFreightRateRequest, relevant_supply_agent_ids=ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, null=True))
    migrator.add_fields(FclFreightRateFeedback, relevant_supply_agent_ids=ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, null=True))


def rollback(migrator: Migrator, database, fake=False, **kwargs):
    pass

