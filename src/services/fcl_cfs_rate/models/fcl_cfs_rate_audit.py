from peewee import * 
from database.db_session import db
from playhouse.postgres_ext import *
import datetime

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class FclCfsRateAudit(BaseModel):
    id = BigAutoField(primary_key=True)
    performed_by_id	= UUIDField(null=True)
    bulk_operation_id = UUIDField(null=True, index=True)
    rate_sheet_id = UUIDField(null=True,index=True)
    object_id = UUIDField(null=True, index=True)
    object_type = CharField(null=True,index=True)
    action_name = CharField(null=True,index=True)
    data = 	BinaryJSONField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(FclCfsRateAudit, self).save(*args, **kwargs)

    class Meta:
        table_name = 'fcl_cfs_rate_audits'