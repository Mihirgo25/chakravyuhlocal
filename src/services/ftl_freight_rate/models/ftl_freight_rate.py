from peewee import *
import datetime
from database.db_session import db
from playhouse.postgres_ext import *
from micro_services.client import *

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class FtlFreightRate(BaseModel):
    id = BigAutoField(primary_key=True)
    service_provider_id = UUIDField(index=True)
    service_provider = BinaryJSONField(null=True)
    importer_exporter_id = UUIDField(null=True)
    importer_exporter = BinaryJSONField(null=True)
    origin_location_id = UUIDField(null=False,index=True)
    origin_location = BinaryJSONField(null=True)
    origin_cluster_id = UUIDField(null=True)
    origin_country_id = UUIDField(null=False,index=True)
    origin_city_id = UUIDField(null=True)
    destination_location_id = UUIDField(null=False,index=True)
    destination_location = BinaryJSONField(null=True)
    destination_cluster_id = UUIDField(null=True)  
    destination_country_id = UUIDField(null=False,index=True)  
    commodity_weight = FloatField(null=False)
    commodity_type = TextField(null=False)
    distance = FloatField()
    line_items = BinaryJSONField(default = [],null = False)
    is_line_items_error_messages_present = BooleanField(null=True)
    is_line_items_info_messages_present = BooleanField(null=True)
    line_items_error_messages = ArrayField(null = False)
    line_items_info_messages = BinaryJSONField(null= True)
    truck_type = CharField(null=False,index = True)
    truck_body_type = CharField(null = False)
    origin_location_type = CharField(null = False)
    destination_location_type = CharField(null = False)
    origin_location_ids = ArrayField(null = False)
    destination_location_ids = ArrayField(null = False) 
    transit_time = CharField(null = False)
    rate_not_available_entry = BooleanField(constraints=[SQL("DEFAULT false")], null=True)
    trip_type = CharField(null = True)
    validity_start = DateTimeField(null = True)
    validity_end = DateTimeField(null= True)
    detention_free_time = CharField(null = True)
    minimum_chargeable_weight = FloatField(null=True)
    source = CharField(null=True)
    sourced_by_id = UUIDField(null=True, index=True)
    procured_by_id = UUIDField(null=True, index=True)
    sourced_by = BinaryJSONField(null=True)
    procured_by = BinaryJSONField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    

    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(FtlFreightRate, self).save(*args, **kwargs)

    class Meta:
        table_name = 'ftl_freight_rates'