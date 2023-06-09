from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
from configs.fcl_freight_rate_constants import *
from database.rails_db import *
import datetime

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class AirCustomsRate(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    airport_id = UUIDField(index=True)
    country_id = UUIDField(index=True)
    trade_id = UUIDField(index=True)
    continent_id = UUIDField(index=True)
    trade_type = CharField(null=True)
    commodity = CharField(null=True, index=True)
    service_provider_id = UUIDField(index=True)
    importer_exporter_id = UUIDField(null=True)
    line_items = BinaryJSONField(null=True)
    platform_price = IntegerField(null=True)
    is_best_price = BooleanField(null=True)
    is_line_items_error_messages_present = BooleanField(null=True)
    is_line_items_info_messages_present = BooleanField(null=True)
    line_items_error_messages = BinaryJSONField(constraints=[SQL("DEFAULT '{}'::jsonb")], null=True)
    line_items_info_messages = BinaryJSONField(constraints=[SQL("DEFAULT '{}'::jsonb")], null=True)
    rate_not_available_entry = BooleanField(constraints=[SQL("DEFAULT false")], null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now, index=True)
    location_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, index=True, null=True)
    rate_type = CharField(index=True, null=True)
    sourced_by_id = UUIDField(null=True, index=True)
    procured_by_id = UUIDField(null=True, index=True)
    sourced_by = BinaryJSONField(null=True)
    procured_by = BinaryJSONField(null=True)
    service_provider = BinaryJSONField(null=True)
    airport = BinaryJSONField(null=True)
    perform_by = BinaryJSONField(null=True)

    class Meta:
        table_name = 'air_customs_rates'

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(AirCustomsRate, self).save(*args, **kwargs)