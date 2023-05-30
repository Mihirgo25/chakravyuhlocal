from peewee import * 
from database.db_session import db
from playhouse.postgres_ext import *
import datetime

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class FclCfsRateAudits(BaseModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4, index=True)
    performed_by_id	= UUIDField(null=True)
    bulk_operation_id = UUIDField(null=True, index=True)
    rate_sheet_id = UUIDField(null=True,index=True)
    object_id = UUIDField(null=True, index=True)
    object_type = CharField(null=True,index=True)
    action_name = CharField(null=True,index=True)
    data = 	BinaryJSONField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    class Meta:
        table_name = 'fcl_cfs_rate_audits'  
        
    def get_audit_params(self):
        audit_data = {
            "line_items": self.line_items,
            "free_days": self.free_days
            }

        return {
            "action_name": 'create',
            "performed_by_id": self.performed_by_id,
            "rate_sheet_id": self.rate_sheet_id,
            "data": audit_data
        }