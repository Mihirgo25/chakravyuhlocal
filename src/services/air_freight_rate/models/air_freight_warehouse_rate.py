from peewee import *
import datetime
from database.db_session import db
from fastapi import HTTPException
from configs.air_freight_rate_constants import MAX_CARGO_LIMIT
from playhouse.postgres_ext import *

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class AirFreightWarehouseRates(BaseModel):
    airport_id = UUIDField(null=True)
    bookings_count = IntegerField(null=True)
    bookings_importer_exporters_count = IntegerField(null=True)
    commodity = CharField(null=True)
    continent_id = UUIDField(null=True)
    country_id = UUIDField(null=True)
    created_at = DateTimeField()
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    importer_exporter_id = UUIDField(null=True)
    is_line_items_error_messages_present = BooleanField(null=True)
    is_line_items_info_messages_present = BooleanField(null=True)
    line_items = BinaryJSONField(null=True)
    line_items_error_messages = BinaryJSONField(null=True)
    line_items_info_messages = BinaryJSONField(null=True)
    location_ids = ArrayField(field_class=UUIDField, index=True, null=True)
    priority_score = IntegerField(null=True)
    priority_score_updated_at = DateTimeField(null=True)
    rate_not_available_entry = BooleanField(constraints=[SQL("DEFAULT false")], null=True)
    service_provider_id = UUIDField(null=True)
    spot_searches_count = IntegerField(null=True)
    spot_searches_importer_exporters_count = IntegerField(null=True)
    trade_id = UUIDField(null=True)
    trade_type = CharField(null=True)
    updated_at = DateTimeField()

    class Meta:
        table_name = 'air_freight_warehouse_rates'