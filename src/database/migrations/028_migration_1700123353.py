"""Peewee migrations -- 028_migration_1700123353.py.

Some examples (model - class or model name)::

    > Model = migrator.orm['model_name']            # Return model in current state by name

    > migrator.sql(sql)                             # Run custom SQL
    > migrator.python(func, *args, **kwargs)        # Run python code
    > migrator.create_model(Model)                  # Create a model (could be used as decorator)
    > migrator.remove_model(model, cascade=True)    # Remove a model
    > migrator.add_fields(model, **fields)          # Add fields to a model
    > migrator.change_fields(model, **fields)       # Change fields
    > migrator.remove_fields(model, *field_names, cascade=True)
    > migrator.rename_field(model, old_field_name, new_field_name)
    > migrator.rename_table(model, new_table_name)
    > migrator.add_index(model, *col_names, unique=False)
    > migrator.drop_index(model, *col_names)
    > migrator.add_not_null(model, *field_names)
    > migrator.drop_not_null(model, *field_names)
    > migrator.add_default(model, field_name, default)

"""

import peewee as pw
from peewee_migrate import Migrator
from decimal import ROUND_HALF_EVEN
from playhouse.postgres_ext import BigIntegerField, BinaryJSONField
from services.air_customs_rate.models.air_customs_rate_feedback import AirCustomsRateFeedback
from services.air_freight_rate.models.air_freight_rate_feedback import AirFreightRateFeedback
from services.fcl_cfs_rate.models.fcl_cfs_rate_feedback import FclCfsRateFeedback
from services.fcl_customs_rate.models.fcl_customs_rate_feedback import FclCustomsRateFeedback
from services.fcl_freight_rate.models.fcl_freight_rate_feedback import FclFreightRateFeedback
from services.ftl_freight_rate.models.ftl_freight_rate_feedback import FtlFreightRateFeedback
from services.haulage_freight_rate.models.haulage_freight_rate_feedback import HaulageFreightRateFeedback

try:
    import playhouse.postgres_ext as pw_pext
except ImportError:
    pass

SQL = pw.SQL


def migrate(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    """Write your migrations here."""
    migrator.add_fields(AirCustomsRateFeedback, spot_search_serial_id = BigIntegerField(null = True))
    migrator.add_fields(AirFreightRateFeedback, spot_search_serial_id = BigIntegerField(null = True))
    migrator.add_fields(FclCfsRateFeedback, spot_search_serial_id = BigIntegerField(null = True))
    migrator.add_fields(FclCustomsRateFeedback, spot_search_serial_id = BigIntegerField(null = True))
    migrator.add_fields(FclFreightRateFeedback, spot_search_serial_id = BigIntegerField(null = True))
    migrator.add_fields(FtlFreightRateFeedback, spot_search_serial_id = BigIntegerField(null = True))
    migrator.add_fields(HaulageFreightRateFeedback, spot_search_serial_id = BigIntegerField(null = True))
    migrator.add_fields(FclFreightRateFeedback, preferred_free_days = BinaryJSONField(null = True))




def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    """Write your rollback migrations here."""
    
