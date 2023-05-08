from enum import unique
from typing import Text
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

class FuelData(BaseModel):
    location_type: CharField(null=False, index = True)
    location_id: UUIDField(null= False , index = True)
    fuel_type: CharField(null = False, index = True)
    fuel_price: DecimalField(null = False)
    currency: CharField(null = False)
    fuel_unit: CharField(null = False)
    created_at: DateTimeField(null = False, default = datetime.datetime.now())
    updated_at: DateTimeField(null = False)

def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(FuelData, self).save(*args, **kwargs)

class Meta:
    table_name = 'fuel_data'