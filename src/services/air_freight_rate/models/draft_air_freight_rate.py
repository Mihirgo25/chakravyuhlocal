from peewee import *
from database.db_session import db
import datetime
from playhouse.postgres_ext import *

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class DraftAirFreightRate(BaseModel):
    id = BigAutoField(primary_key=True)
    rate_id = UUIDField(null=True)
    origin_airport_id = UUIDField(null=False, index=True)
    destination_airport_id = UUIDField(null=False, index=True)
    weight_slabs = BinaryJSONField(null=False, index=False)
    min_price = FloatField(null=False, default=0.0)
    meta_data = BinaryJSONField(null=True)
    commodity = TextField(null=False, index=True)
    commodity_type = TextField(null=True)
    operation_type = TextField(null=False, index=True)
    price_type = TextField(null=False, index=True)
    rate_type = TextField(null=True)
    service_provider_id = UUIDField(null=False, index=True)
    airline_id = UUIDField(null=False, index=True)
    currency = TextField(null=False)
    stacking_type = TextField(null=False, index=True)
    status = TextField(default='active', null=False, index=True)
    source = TextField(null=False, index=True)
    validity_start = DateField(index=True, null=True)
    validity_end = DateField(index=True, null=True)
    created_at = DateTimeField(default=datetime.datetime.now, index = True)
    updated_at = DateTimeField(default=datetime.datetime.now, index = True)
    
    class Meta:
        table_name = 'draft_air_freight_rates'
