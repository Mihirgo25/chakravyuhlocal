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
    id = BigAutoField(primary_key=True)
    truck_company = TextField(null=True)
    truck_name = CharField(null=False)
    display_name = CharField(null=False)
    created_at = DateTimeField(default=datetime.datetime.now, index=True)
    mileage = FloatField(null=True)
    mileage_unit = CharField(null=True,index = True)
    capacity = FloatField(null=True, index=True)
    capacity_unit = TextField(null=True,index= True)
    vehicle_weight = FloatField(null=True, index=True)
    vehicle_weight_unit = TextField(null=True,index=True)
    fuel_type = TextField(null=True,index=True)
    avg_speed = FloatField(null=True)
    no_of_wheels = IntegerField(null=True)
    engine_type = TextField(null=True)
    country_id = UUIDField(null=True,index=True)
    axels = IntegerField(null=True)
    truck_type = TextField(null=True,index=True)
    body_type = TextField(null=True,index=True)
    status = TextField(null=True)
    horse_power = FloatField(null=True)
    updated_at = DateTimeField(default=datetime.datetime.now, index=True)
    data = BinaryJSONField(null=True)
    search_vector = TSVectorField(
        constraints=[SQL(
            """GENERATED ALWAYS AS (
                setweight(to_tsvector('english', coalesce(truck_company, '')),'C') ||
                setweight(to_tsvector('english', coalesce(truck_name, '')),'C') ||
                setweight(to_tsvector('english', coalesce(display_name, '')),'A') ||
                setweight(to_tsvector('english', coalesce(cast(mileage as text), '')),'D') ||
                setweight(to_tsvector('english', coalesce(cast(capacity as text), '')),'B') ||
                setweight(to_tsvector('english', coalesce(fuel_type, '')),'B') ||
                setweight(to_tsvector('english', coalesce(cast(no_of_wheels as text), '')),'D') ||
                setweight(to_tsvector('english', coalesce(truck_type, '')),'B') ||
                setweight(to_tsvector('english', coalesce(body_type, '')),'C')
                )
            STORED"""
            )]
        )

    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(Truck, self).save(*args, **kwargs)

    class Meta:
        table_name = 'trucks'
