from peewee import *
from database.db_session import db 
from playhouse.postgres_ext import BinaryJSONField
import datetime

class BaseModel(Model):
    class Meta:
        database = db 

class FreightTrendAudit(BaseModel):
    id = UUIDField(primary_key=True,constraints=[SQL("DEFAULT gen_random_uuid()")])
    object_type = TextField(null=True)
    object_id = UUIDField(null=True)
    action_name = TextField(null=True)
    performed_by_id = UUIDField(null=True)
    data = BinaryJSONField(null = True)
    created_at = DateTimeField(default = datetime.datetime.now())
    updated_at = DateTimeField(default = datetime.datetime.now())

    class Meta:
        table_name = 'freight_trend_audits'
