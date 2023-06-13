from peewee import *
from datetime import datetime,timedelta
from database.db_session import db
from playhouse.postgres_ext import *

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class AirFreightRateAudits(BaseModel):
    action_name = CharField(null=True)
    bulk_operation_id = UUIDField(index=True, null=True)
    created_at = DateTimeField(default=datetime.now(),index=True)
    data = BinaryJSONField(null=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    object_id = UUIDField(null=True,index=True)
    object_type = CharField(null=True,index = True)
    performed_by_id = UUIDField(index=True)
    # performed_by:BinaryJSONField(null=True)
    rate_sheet_id = UUIDField(index=True, null=True)
    updated_at = DateTimeField(default=datetime.now(),index=True)
    validity_id = UUIDField(null=True,index=True)

    class Meta:
        table_name = 'air_freight_rate_audits'
