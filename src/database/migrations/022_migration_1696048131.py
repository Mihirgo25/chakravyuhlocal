import peewee as pw
from peewee_migrate import Migrator
from peewee import *
from playhouse.postgres_ext import *
try:
    import playhouse.postgres_ext as pw_pext
except ImportError:
    pass
from services.air_freight_rate.models.air_freight_rate_jobs import AirFreightRateJob
from services.fcl_freight_rate.models.fcl_freight_rate_jobs import FclFreightRateJob
from services.fcl_freight_rate.models.fcl_freight_rate_job_mappings import FclFreightRateJobMapping
from services.air_freight_rate.models.air_freight_rate_jobs_mapping import AirFreightRateJobMapping

SQL = pw.SQL


def migrate(migrator: Migrator, database, fake=False, **kwargs):
    """Write your migrations here."""
    migrator.add_fields(AirFreightRateJob, is_visible = BooleanField(default=True))
    migrator.add_fields(FclFreightRateJob, is_visible = BooleanField(default=True))
    migrator.add_fields(AirFreightRateJob, cogo_entity_id = UUIDField(null=True, index=True))
    migrator.add_fields(FclFreightRateJob, cogo_entity_id = UUIDField(null=True, index=True))
    migrator.add_fields(FclFreightRateJobMapping, status = TextField(null=True, index=True))
    migrator.add_fields(AirFreightRateJobMapping, status = TextField(null=True, index=True))
    migrator.add_fields(FclFreightRateJob, search_source = TextField(null=True, index=True))
    migrator.add_fields(AirFreightRateJob, search_source = TextField(null=True, index=True))
    migrator.add_fields(FclFreightRateJobMapping, shipment_id = UUIDField(null=True, index=True))
    migrator.add_fields(AirFreightRateJobMapping, shipment_id = UUIDField(null=True, index=True))
    migrator.add_fields(FclFreightRateJobMapping, shipment_serial_id = BigIntegerField(index=True, null=True))
    migrator.add_fields(AirFreightRateJobMapping, shipment_serial_id = BigIntegerField(index=True, null=True))
    migrator.add_fields(FclFreightRateJobMapping, shipment_service_id = UUIDField(index=True, null=True))
    migrator.add_fields(AirFreightRateJobMapping, shipment_service_id = UUIDField(index=True, null=True))
    
def rollback(migrator: Migrator, database, fake=False, **kwargs):
    pass

