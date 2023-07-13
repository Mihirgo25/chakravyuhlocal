from peewee_migrate import Migrator
from services.fcl_freight_rate.models.fcl_freight_rate_feedback import FclFreightRateFeedback
from services.fcl_freight_rate.models.fcl_freight_rate_request import FclFreightRateRequest
from peewee import *
from playhouse.postgres_ext import *

def migrate(migrator: Migrator, database, fake=False, **kwargs):
    """Write your migrations here."""
    migrator.add_fields(FclFreightRateFeedback, attachment_file_urls=ArrayField(constraints=[SQL("DEFAULT '{}'::character varying[]")], field_class=TextField, null=True))
    migrator.add_fields(FclFreightRateRequest, attachment_file_urls=ArrayField(constraints=[SQL("DEFAULT '{}'::character varying[]")], field_class=TextField, null=True))
    migrator.add_fields(FclFreightRateRequest, commodity_description=CharField(null=True))
    migrator.add_fields(FclFreightRateFeedback, commodity_description=CharField(null=True))

def rollback(migrator: Migrator, database, fake=False, **kwargs):
    """Write your rollback migrations here."""
