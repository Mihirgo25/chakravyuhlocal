from peewee import * 
from database.db_session import db
from playhouse.postgres_ext import *
import datetime

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True
        
class DraftFclFreightRate(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    rate_id = UUIDField(index=True, null=False)
    data = BinaryJSONField(constraints=[SQL("DEFAULT '{}'::jsonb")], null=True)
    source = CharField(null=False)
    status = CharField(null=False)
    invoice_url = TextField(null=True, index=True)
    invoice_date = DateField(null=True)
    shipment_serial_id = BigIntegerField(null=True, index= False)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now, index=True)
    
    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(DraftFclFreightRate, self).save(*args, **kwargs)

    class Meta:
        table_name = 'draft_fcl_freight_rates'