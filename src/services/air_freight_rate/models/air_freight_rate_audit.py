from peewee import * 
from database.db_session import db
from playhouse.postgres_ext import *
import datetime

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class AirFreightRateAudit(BaseModel):
    action_name = CharField(null=True)
    bulk_operation_id = UUIDField(index=True, null=True)
    created_at = DateTimeField(default=datetime.datetime.now, index=True)
    data = BinaryJSONField(null=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    object_id = UUIDField(index=True, null=True)
    object_type = CharField(null=True)
    performed_by_id = UUIDField(index=True)
    rate_sheet_id = UUIDField(index=True, null=True)
    source = CharField(null=True)
    updated_at = DateTimeField(default=datetime.datetime.now)
    validity_id = UUIDField(null=True,index=True)
    performed_by_type = CharField(index=True,null=True)
    
    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(AirFreightRateAudit, self).save(*args, **kwargs)
    
    class Meta:
        table_name = 'air_freight_rate_audits'
        