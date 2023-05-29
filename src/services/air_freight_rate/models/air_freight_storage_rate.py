from peewee import * 
import datetime
from database.db_session import db
from playhouse.postgres_ext import *

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True
class AirFreightStorageRates(BaseModel):
    airline_id = UUIDField(null=True)
    airport_id = UUIDField(null=True)
    commodity = CharField(null=True)
    continent_id = UUIDField(null=True)
    country_id = UUIDField(null=True)
    created_at = DateTimeField()
    free_limit = IntegerField(null=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    importer_exporter_id = UUIDField(null=True)
    is_slabs_missing = BooleanField(null=True)
    location_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, index=True, null=True)
    priority_score = IntegerField(null=True)
    priority_score_updated_at = DateTimeField(null=True)
    remarks = ArrayField(constraints=[SQL("DEFAULT '{}'::character varying[]")], field_class=CharField, null=True)
    service_provider_id = UUIDField(null=True)
    slabs = BinaryJSONField(null=True)
    trade_id = UUIDField(null=True)
    trade_type = CharField(null=True)
    updated_at = DateTimeField()

    class Meta:
        table_name = 'air_freight_storage_rates'
        indexes = (
            (('airport_id', 'airline_id', 'commodity', 'trade_type'), False),
            (('airport_id', 'airline_id', 'trade_type', 'commodity', 'service_provider_id', 'importer_exporter_id'), True),
        )