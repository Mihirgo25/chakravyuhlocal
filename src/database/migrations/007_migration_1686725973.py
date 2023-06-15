"""Peewee migrations -- 007_migration_1686719978.py.

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
from peewee import *

from playhouse.postgres_ext import *

from services.fcl_freight_rate.models.fcl_freight_rate_audit import FclFreightRateAudit

try:
    import playhouse.postgres_ext as pw_pext
except ImportError:
    pass

SQL = pw.SQL


def migrate(migrator: Migrator, database, fake=False, **kwargs):
    migrator.add_fields(FclFreightRateAudit, extended_from_object_id=UUIDField(index=True,null=True))  
    migrator.sql('Create index fcl_freight_rate_audit_source on fcl_freight_rate_audits (source) ;')
    migrator.sql('Create index fcl_freight_rate_audit_extended_from_object_id on fcl_freight_rate_audits (extended_from_object_id) ;')
def rollback(migrator: Migrator, database, fake=False, **kwargs):
    pass