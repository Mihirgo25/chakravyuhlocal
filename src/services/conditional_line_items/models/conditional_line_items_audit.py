from peewee import * 
from database.db_session import db
from playhouse.postgres_ext import *
import datetime

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class ConditionalLineItemAudit(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    action_name = CharField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now, index=True)
    data = BinaryJSONField(null=True)
    object_id = IntegerField(index=True)
    performed_by_id = UUIDField(index=True,null=True)
    rate_sheet_id = UUIDField(index=True, null=True)
    updated_at = DateTimeField(default=datetime.datetime.now, index=True)
    
    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(ConditionalLineItemAudit, self).save(*args, **kwargs)

    class Meta:
        table_name = 'conditional_line_item_audits'