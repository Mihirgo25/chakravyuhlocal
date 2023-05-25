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

class AirFreightRateLocal(BaseModel):
    airline_id = UUIDField(null=True)
    airport_id = UUIDField(null=True)
    bookings_count = IntegerField(null=True)
    bookings_importer_exporters_count = IntegerField(null=True)
    commodity = CharField(null=True)
    commodity_type = CharField(null=True)
    continent_id = UUIDField(null=True)
    country_id = UUIDField(null=True)
    created_at = DateTimeField()
    currency = CharField(null=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    is_line_items_error_messages_present = BooleanField(null=True)
    is_line_items_info_messages_present = BooleanField(null=True)
    line_items = BinaryJSONField(null=True)
    line_items_error_messages = BinaryJSONField(null=True)
    line_items_info_messages = BinaryJSONField(null=True)
    location_ids = ArrayField(field_class=UUIDField, index=True, null=True)
    min_price = DecimalField(null=True)
    priority_score = IntegerField(null=True)
    priority_score_updated_at = DateTimeField(null=True)
    service_provider_id = UUIDField(null=True)
    spot_searches_count = IntegerField(null=True)
    spot_searches_importer_exporters_count = IntegerField(null=True)
    storage_rate_id = UUIDField(null=True)
    trade_id = UUIDField(null=True)
    trade_type = CharField(null=True)
    updated_at = DateTimeField()

    class Meta:
        table_name = 'air_freight_rate_locals'
        indexes = (
            (('priority_score', 'id', 'service_provider_id'), False),
            (('priority_score', 'service_provider_id'), False),
            (('updated_at', 'id', 'service_provider_id'), False),
            (('updated_at', 'service_provider_id'), False),
        )
    