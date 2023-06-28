from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
import datetime

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class FclCustomsRateAudit(BaseModel):
    id = BigAutoField(primary_key=True)
    bulk_operation_id = UUIDField(index=True, null=True)
    rate_sheet_id = UUIDField(index=True, null=True)
    object_type = CharField(null=True)
    object_id = UUIDField(index=True, null=True)
    action_name = CharField(null=True)
    performed_by_id = UUIDField(index=True, null =True)
    data = BinaryJSONField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now, index=True)
    updated_at = DateTimeField(default=datetime.datetime.now)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(FclCustomsRateAudit, self).save(*args, **kwargs)

    class Meta:
        table_name = 'fcl_customs_rate_audits'