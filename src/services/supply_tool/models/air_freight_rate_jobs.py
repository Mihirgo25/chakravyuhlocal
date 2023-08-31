from peewee import *
import datetime
from database.db_session import db
from playhouse.postgres_ext import *
from micro_services.client import *
from database.rails_db import *

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True


class AirFreightRateJobs(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    user_id = UUIDField(null=True)
    origin_airport = BinaryJSONField(null=True)
    origin_airport_id = UUIDField(null=True, index=True)
    destination_airport = BinaryJSONField(null=True)
    destination_airport_id = UUIDField(null=True, index=True)
    service_provider = BinaryJSONField(null=True)
    service_provider_id = UUIDField(null=True, index=True)
    airline = BinaryJSONField(null=True)
    airline_id = UUIDField(null=True, index=True)
    breadth = IntegerField(null=True)
    height = IntegerField(null=True)
    length = IntegerField(null=True)
    commodity = CharField(null=True, index=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    status = CharField(index=True, null=True)
    source = TextField(null=True, index=True)
    assigned_to_id = UUIDField(index=True, null=True)
    assigned_to = BinaryJSONField(null=True)
    closed_by_id = UUIDField(null=True, index=True)
    closed_by = BinaryJSONField(null=True)
    closing_remarks = TextField(null=True)    
    shipment_type = CharField(null=True)
    stacking_type = CharField(null=True, index=True)

    class Meta:
        table_name = 'air_freight_rate_jobs'

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(AirFreightRateJobs, self).save(*args, **kwargs)