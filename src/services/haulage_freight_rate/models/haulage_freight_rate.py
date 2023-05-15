from peewee import *
from database.db_session import db
import uuid
import datetime
from playhouse.postgres_ext import *



class BaseModel(Model):
    class Meta:
        database = db
class HaulageFreightRate(BaseModel):
    id = UUIDField(
        primary_key=True,
        constraints=[SQL("DEFAULT uuid_generate_v4()")],
        default=uuid.uuid4,
    )
    origin_location_id = UUIDField(null=True)
    origin_cluster_id = UUIDField(null=True)
    origin_city_id = UUIDField(null=True)
    destination_location_id = UUIDField(null=True)
    destination_cluster_id = UUIDField(null=True)
    destination_city_id = UUIDField(null=True)
    container_size = IntegerField(index=True, null=True)
    commodity_type = CharField(index=True, null=True)
    commodity = CharField(index=True, null=True)
    importer_exporter_id = UUIDField(null=True)
    service_provider_id = UUIDField(null=True)
    container_count =  IntegerField(index=True, null=True)
    importer_exporter_count = IntegerField(index=True, null=True)
    weight_slabs = BinaryJSONField(index=True, null=True)
    line_items = BinaryJSONField(index=True, null=True)
    is_best_price = BooleanField(index=True, null=True)
    is_line_items_error_messages_present = BooleanField(index=True, null=False)
    is_line_items_info_messages_present = BooleanField(index=True, null=False)
    line_items_error_messages = BinaryJSONField(index=True, null=True)
    line_items_info_messages = BinaryJSONField(index=True, null=True)
    rate_not_available_entry = BooleanField(index=True, null=False)
    trip_type = CharField(index=True, null=True)
    validity_start = DateTimeField(default=datetime.datetime.now)
    validity_end = DateTimeField(default = datetime.datetime.now() - datetime.timedelta(30))
    detention_free_time = IntegerField(index=True, null=True)
    transit_time = IntegerField(index=True, null=True)
    platform_price = FloatField(index=True, null=True)
    haulage_type = CharField(index=True, null=True, default='merchant')
    transport_modes = BinaryJSONField(index=True, null=True)
    destination_country_id = UUIDField(null=True)
    origin_country_id = UUIDField(null=True)
    shipping_line_id = UUIDField(null=True)
    origin_destination_location_type = CharField(index=True, null=True)
    destination_location_type = CharField(index=True, null=True)
    origin_location_type = CharField(index=True, null=True)
    origin_location_ids = ArrayField(UUIDField, null=True)
    destination_location_ids = ArrayField(UUIDField, null=True)
    created_at = DateTimeField(default=datetime.datetime.now, index=True)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = 'haulage_freight_rate'

    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(HaulageFreightRate, self).save(*args, **kwargs)
