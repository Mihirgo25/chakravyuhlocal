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

class Trailer(BaseModel):
    name = CharField(null=False)
    created_at = DateTimeField(default=datetime.datetime.now, index=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    length = FloatField(null=True)
    breadth = FloatField(null=True)
    height = FloatField(null=True)
    capacity = FloatField(null=True)
    capacity_unit = TextField(null=True)
    no_of_tyres = IntegerField(null=True)
    country_id = UUIDField(null=True)
    country = BinaryJSONField(null=True)
    axels = IntegerField(null=True)
    trailer_type = TextField(null=True)
    body_type = TextField(null=True)
    status = TextField(null=True)
    updated_at = DateTimeField(default=datetime.datetime.now, index=True)
    
    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(Trailer, self).save(*args, **kwargs)

    class Meta:
        table_name = 'trailers'