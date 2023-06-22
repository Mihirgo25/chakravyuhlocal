import peewee as pw
from peewee_migrate import Migrator
from services.fcl_freight_rate.models.fcl_freight_rate_feedback import FclFreightRateFeedback
from services.fcl_freight_rate.models.fcl_freight_rate_request import FclFreightRateRequest
from playhouse.postgres_ext import *

SQL = pw.SQL


def migrate(migrator: Migrator, database, fake=False, **kwargs):
    migrator.sql('ALTER TABLE fcl_freight_rate_feedbacks ALTER COLUMN commodity_description TYPE text;')
    migrator.sql('ALTER TABLE fcl_freight_rate_requests ALTER COLUMN commodity_description TYPE text;')
    migrator.sql("ALTER TABLE fcl_freight_rate_feedbacks ALTER COLUMN remarks SET DEFAULT '{}'::text[];")
    migrator.sql("ALTER TABLE fcl_freight_rate_feedbacks ALTER COLUMN closing_remarks SET DEFAULT '{}'::text[];")
    migrator.sql("ALTER TABLE fcl_freight_rate_feedbacks ALTER COLUMN feedbacks SET DEFAULT '{}'::text[];")
    migrator.sql("ALTER TABLE fcl_freight_rate_feedbacks ALTER COLUMN attachment_file_urls SET DEFAULT '{}'::text[];")
    migrator.sql("ALTER TABLE fcl_freight_rate_requests ALTER COLUMN attachment_file_urls SET DEFAULT '{}'::text[];")
    migrator.sql("ALTER TABLE fcl_freight_rate_requests ALTER COLUMN remarks SET DEFAULT '{}'::text[];")
    migrator.sql("ALTER TABLE fcl_freight_rate_requests ALTER COLUMN closing_remarks SET DEFAULT '{}'::text[];")


def rollback(migrator: Migrator, database, fake=False, **kwargs):
    pass

