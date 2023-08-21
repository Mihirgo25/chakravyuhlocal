import peewee as pw
from peewee_migrate import Migrator
from services.bramhastra.models.fcl_freight_rate_statistic import FclFreightRateStatistic
from peewee import UUIDField,CharField

SQL = pw.SQL


def migrate(migrator: Migrator, database, fake=False, **kwargs):
    """Write your migrations here."""
    migrator.add_fields(FclFreightRateStatistic, performed_by_id = UUIDField(null=True))
    migrator.add_fields(FclFreightRateStatistic, performed_by_type = CharField(null=True))
    migrator.add_fields(FclFreightRateStatistic, rate_sheet_id= UUIDField(null=True))
    migrator.add_fields(FclFreightRateStatistic, bulk_operation_id = UUIDField(null=True))
    



def rollback(migrator: Migrator, database, fake=False, **kwargs):
    """Write your rollback migrations here."""