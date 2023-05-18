from peewee import *
import datetime
from database.db_session import db
from playhouse.postgres_ext import *
from micro_services.client import *

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class FtlFreightRateRuleSet(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    location_id = UUIDField(null=False,index=True)
    location_type = CharField(null=False,index = True)
    truck_type = CharField(null=False,index = True)
    process_type = TextField(null=False,index = True)
    process_unit = CharField(null=False,index = True)
    process_value = DecimalField(null=False,max_digits=20,decimal_places=10)
    process_currency = CharField(null=False)
    status = CharField(null=False)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    

    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(FtlFreightRateRuleSet, self).save(*args, **kwargs)

    class Meta:
        table_name = 'ftl_freight_rates'