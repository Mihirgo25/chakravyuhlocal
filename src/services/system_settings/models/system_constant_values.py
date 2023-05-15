from peewee import *
from database.db_session import db
import datetime
from playhouse.postgres_ext import *


class BaseModel(Model):
    class Meta:
        database = db


class SystemConstantValue(BaseModel):
    id = BigAutoField(primary_key=True)
    value = BinaryJSONField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    status = TextField(default="active", null=False)
    search_vector = TSVectorField(constraints=[SQL("GENERATED ALWAYS AS (to_tsvector('english', coalesce(name, ''))) STORED")])

    class Meta:
        table_name = "system_constant_values"

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(SystemConstantValue, self).save(*args, **kwargs)
