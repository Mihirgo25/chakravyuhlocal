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

class Truck(BaseModel):
    truck_company = TextField(null=True)
    name = CharField(null=False)
    created_at = DateTimeField(default=datetime.datetime.now, index=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    length = FloatField(null=True)
    breadth = FloatField(null=True)
    height = FloatField(null=True)
    milage = FloatField(null=True)
    milgae_unit = TextField(null=True)
    capacity = FloatField(null=True)
    capacity_unit = TextField(null=True)
    vehicle_weight = FloatField(null=True)
    fuel_type = TextField(null=True)
    avg_speed = FloatField(null=True)
    no_of_tyres = IntegerField(null=True)
    engine_type = TextField(null=True)
    country_id = UUIDField(null=True)
    country = BinaryJSONField(null=True)
    axels = IntegerField(null=True)
    truck_type = TextField(null=True)
    body_type = TextField(null=True)
    status = TextField(null=True)
    delivery_type = TextField(null=True)
    horse_power = FloatField(null=True)
    door_width = FloatField(null=True)
    door_height = FloatField(null=True)
    chasis = TextField(null=True)
    updated_at = DateTimeField(default=datetime.datetime.now, index=True)
    
    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(Truck, self).save(*args, **kwargs)

    class Meta:
        table_name = 'trucks'