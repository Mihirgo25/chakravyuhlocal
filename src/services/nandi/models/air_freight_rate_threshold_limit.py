from peewee import *
import datetime
from database.db_session import db
from playhouse.postgres_ext import *

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class AirFreightRateThresholdLimit(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    airline_id = UUIDField(index=True, null=True)
    origin_airport_id = UUIDField(index=True, null=True)
    destination_airport_id = UUIDField(index=True, null=True)
    min_threshold = FloatField(null = True)
    max_threshold = FloatField(null = True)
    min_threshold_type = CharField(null=True)
    max_threshold_type = CharField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(AirFreightRateThresholdLimit, self).save(*args, **kwargs)

    class Meta:
        table_name = 'air_freight_rate_threshold_limits'