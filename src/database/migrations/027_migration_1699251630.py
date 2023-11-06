"""Peewee migrations -- 027_migration_1699251630.py.

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

import datetime as dt
import peewee as pw
from peewee_migrate import Migrator
from decimal import ROUND_HALF_EVEN
from services.air_freight_rate.models.air_freight_rate_request import AirFreightRateRequest
from services.fcl_freight_rate.models.fcl_freight_rate_request import FclFreightRateRequest
from services.ftl_freight_rate.models.ftl_freight_rate_request import FtlFreightRateRequest
from services.haulage_freight_rate.models.haulage_freight_rate_request import HaulageFreightRateRequest


from playhouse.postgres_ext import BinaryJSONField

try:
    import playhouse.postgres_ext as pw_pext
except ImportError:
    pass

SQL = pw.SQL


def migrate(migrator: Migrator, database, fake=False, **kwargs):
    migrator.add_fields(AirFreightRateRequest, reverted_rates = BinaryJSONField(null= True))
    migrator.add_fields(FclFreightRateRequest, reverted_rates = BinaryJSONField(null= True))
    migrator.add_fields(FtlFreightRateRequest, reverted_rates = BinaryJSONField(null= True))
    migrator.add_fields(HaulageFreightRateRequest, reverted_rates = BinaryJSONField(null= True))

    """Write your migrations here."""



def rollback(migrator: Migrator, database, fake=False, **kwargs):
    """Write your rollback migrations here."""

