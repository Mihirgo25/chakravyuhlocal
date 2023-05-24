from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
import datetime

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class FclCustomsRate(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    location_id = UUIDField(index=True)
    country_id = UUIDField(index=True)
    trade_id = UUIDField(index=True)
    continent_id = UUIDField(index=True)
    trade_type = CharField(null=True)
    container_size = CharField(null=True, index=True)
    container_type = CharField(null=True, index=True)
    commodity = CharField(null=True, index=True)
    service_provider_id = UUIDField(index=True)
    importer_exporter_id = UUIDField(index=True)
    containers_count = IntegerField(null=True)
    importer_exporters_count = IntegerField(null=True)
    customs_line_items = BinaryJSONField(null=True)
    cfs_line_items = BinaryJSONField(null=True)
    platform_price = IntegerField(null=True)
    is_best_price = BooleanField(null=True)
    is_customs_line_items_error_messages_present = BooleanField(null=True)
    is_customs_line_items_info_messages_present = BooleanField(null=True)
    customs_line_items_error_messages = BinaryJSONField(constraints=[SQL("DEFAULT '{}'::jsonb")], null=True)
    customs_line_items_info_messages = BinaryJSONField(constraints=[SQL("DEFAULT '{}'::jsonb")], null=True)
    is_cfs_line_items_error_messages_present = BooleanField(null=True)
    is_cfs_line_items_info_messages_present = BooleanField(null=True)
    cfs_line_items_error_messages = BinaryJSONField(constraints=[SQL("DEFAULT '{}'::jsonb")], null=True)
    cfs_line_items_info_messages = BinaryJSONField(constraints=[SQL("DEFAULT '{}'::jsonb")], null=True)
    rate_not_available_entry = BooleanField(constraints=[SQL("DEFAULT false")], null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now, index=True)
    location_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, index=True, null=True)
    location_type = CharField(index=True, null=True)

    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(FclCustomsRate, self).save(*args, **kwargs)


    class Meta:
        table_name = 'fcl_customs_rates'