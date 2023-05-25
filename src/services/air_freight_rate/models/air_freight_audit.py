from peewee import *
from datetime import datetime,timedelta
from database.db_session import db



class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class AirFreightRateAudits(BaseModel):
    action_name = CharField(null=True)
    bulk_operation_id = UUIDField(index=True, null=True)
    created_at = DateTimeField()
    data = BinaryJSONField(null=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    object_id = UUIDField(null=True)
    object_type = CharField(null=True)
    performed_by_id = UUIDField(null=True)
    rate_sheet_id = UUIDField(index=True, null=True)
    updated_at = DateTimeField()
    validity_id = UUIDField(null=True)

    class Meta:
        table_name = 'air_freight_rate_audits'
        indexes = (
            (('object_type', 'object_id'), False),
        )