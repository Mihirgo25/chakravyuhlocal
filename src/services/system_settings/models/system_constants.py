from peewee import *
from database.db_session import db
import datetime
from playhouse.postgres_ext import *


class BaseModel(Model):
    class Meta:
        database = db


class SystemConstant(BaseModel):
    id = BigAutoField(primary_key=True)
    name = TextField(unique=True, null=False, index=True)
    data_type = TextField(null=False)

    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    status = TextField(default="active", null=False)
    search_vector = TSVectorField(constraints=[SQL("GENERATED ALWAYS AS (to_tsvector('english', coalesce(name, ''))) STORED")])

    class Meta:
        table_name = "system_constants"

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(SystemConstant, self).save(*args, **kwargs)
