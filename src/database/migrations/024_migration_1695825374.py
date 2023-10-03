from contextlib import suppress
from services.nandi.models.draft_fcl_freight_rate_local import DraftFclFreightRateLocal
import peewee as pw
from peewee_migrate import Migrator
from playhouse.postgres_ext import *

with suppress(ImportError):
    import playhouse.postgres_ext as pw_pext


def migrate(migrator: Migrator, database: pw.Database, *, fake=False):
    """Write your migrations here."""
    migrator.sql("Create index draft_fcl_freight_rate_locals_status on draft_fcl_freight_rate_locals (status) ;")
    migrator.sql("Create index draft_fcl_freight_rate_locals_shipment_serial_id on draft_fcl_freight_rate_locals (shipment_serial_id) ;")
    migrator.sql("ALTER TABLE draft_fcl_freight_rate_locals ALTER COLUMN invoice_url SET DEFAULT '{}'::text[];")
    migrator.sql("ALTER TABLE draft_fcl_freight_rate_locals ALTER COLUMN invoice_date SET DEFAULT '{}'::date[];")
    migrator.add_fields(DraftFclFreightRateLocal, performed_by_id = UUIDField(index=True,null=True)) 
    migrator.add_fields(DraftFclFreightRateLocal, performed_by = BinaryJSONField(null=True))

    


def rollback(migrator: Migrator, database: pw.Database, *, fake=False):
    pass