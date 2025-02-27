import datetime
from peewee import *
from fastapi import HTTPException
from database.db_session import db
from playhouse.postgres_ext import *


class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class FclFreightRateEstimationRatio(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    origin_port_id = UUIDField(index=True)
    destination_port_id = UUIDField(index=True)
    commodity = CharField(index=True)
    container_size = CharField(index=True)
    container_type = CharField(index=True)
    shipping_line_id = UUIDField(index=True)
    sl_weighted_ratio = FloatField(index=True)
    created_at = DateTimeField(default=datetime.datetime.now, index=True)
    updated_at = DateTimeField(default=datetime.datetime.now, index=True)
    
    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(FclFreightRateEstimationRatio, self).save(*args, **kwargs)

    class Meta:
        table_name = 'fcl_freight_rate_estimation_ratios'