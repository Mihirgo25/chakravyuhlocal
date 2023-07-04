from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
import datetime

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class HaulageFreightRateAudit(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    bulk_operation_id = UUIDField(index=True, null=True)
    rate_sheet_id = UUIDField(index=True, null=True)
    object_type = CharField(null=True)
    object_id = UUIDField(index=True, null=True)
    action_name = CharField(null=True)
    performed_by_id = UUIDField(index=True, null =True)
    procured_by_id = UUIDField(index=True, null =True)
    sourced_by_id = UUIDField(index=True, null =True)
    data = BinaryJSONField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now, index=True)
    updated_at = DateTimeField(default=datetime.datetime.now)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(HaulageFreightRateAudit, self).save(*args, **kwargs)

    class Meta:
        table_name = 'haulage_freight_rate_audits'