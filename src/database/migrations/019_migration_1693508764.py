"""Peewee migrations -- 011_migration_1687793137.py.

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
from peewee import *
from playhouse.postgres_ext import *
try:
    import playhouse.postgres_ext as pw_pext
except ImportError:
    pass
from services.bramhastra.models.air_freight_rate_statistic import AirFreightRateStatistic
from services.bramhastra.models.fcl_freight_rate_statistic import FclFreightRateStatistic
from datetime import datetime

SQL = pw.SQL


def migrate(migrator: Migrator, database, fake=False, **kwargs):
    """Write your migrations here."""
    migrator.add_fields(FclFreightRateStatistic,is_deleted = BooleanField(index = True,default = False))
    migrator.add_fields(AirFreightRateStatistic,operation_created_at = DateTimeTZField(default = datetime.utcnow()))
    migrator.add_fields(AirFreightRateStatistic,operation_updated_at = DateTimeTZField(default = datetime.utcnow()))
    migrator.add_fields(AirFreightRateStatistic,is_deleted = BooleanField(index = True,default = False))


def rollback(migrator: Migrator, database, fake=False, **kwargs):
    pass