"""Peewee migrations -- 024_migration_1696931693.py.

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

try:
    import playhouse.postgres_ext as pw_pext
except ImportError:
    pass

SQL = pw.SQL


def migrate(migrator: Migrator, database, fake=False, **kwargs):
    """Write your migrations here."""
    migrator.sql("CREATE INDEX air_customs_rate_feedbacks_serial_id ON air_customs_rate_feedbacks(serial_id);")
    migrator.sql("CREATE INDEX fcl_freight_rate_feedbacks_serial_id ON fcl_freight_rate_feedbacks(serial_id);")
    migrator.sql("CREATE INDEX air_freight_rate_requests_serial_id ON air_freight_rate_requests(serial_id);")
    migrator.sql("CREATE INDEX fcl_freight_rate_requests_serial_id ON fcl_freight_rate_requests(serial_id);")
    
    
def rollback(migrator: Migrator, database, fake=False, **kwargs):
    """Write your rollback migrations here."""

