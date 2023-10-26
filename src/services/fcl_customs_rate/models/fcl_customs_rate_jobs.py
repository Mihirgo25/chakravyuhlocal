from peewee import *
import datetime
from database.db_session import db
from playhouse.postgres_ext import *
from fastapi import HTTPException
from params import Slab
from micro_services.client import *
from database.rails_db import *
from micro_services.client import maps

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class FclCustomsRateJob(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    location = BinaryJSONField(null=True)
    location_id = UUIDField(index=True)
    trade_type = CharField(null=True)
    service_provider_id = UUIDField(null=True, index=True)
    service_provider = BinaryJSONField(null=True)
    container_size = CharField(null=True, index=True)
    container_type = CharField(null=True, index=True)
    commodity = CharField(null=True, index=True)
    sources = ArrayField(constraints=[SQL("DEFAULT '{}'::text[]")], field_class=TextField, null=True)
    user_id = UUIDField(index=True, null=True)
    assigned_to = BinaryJSONField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now, index=True)
    updated_at = DateTimeField(default=datetime.datetime.now, index=True)
    status = CharField(index=True, null=True)
    closed_by_id = UUIDField(null=True, index=True)
    closed_by = BinaryJSONField(null=True)
    closing_remarks = TextField(null=True)
    rate_type = TextField(null=True)
    init_key = TextField(index=True, null=True)
    is_visible = BooleanField(default=True)
    cogo_entity_id = UUIDField(null=True, index=True)
    serial_id = BigIntegerField(constraints=[SQL("DEFAULT nextval('fcl_customs_rate_jobs_serial_id_seq')")],)
    search_source = TextField(null=True, index=True)

    class Meta:
        table_name = 'fcl_customs_rate_jobs'

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(FclCustomsRateJob, self).save(*args, **kwargs)

    def set_locations(self):
      ids = self.location_id
      obj = {'filters':{"id": ids, "type":'seaport'}, 'includes': {"id": True, "name": True, "is_icd": True, "port_code": True, "country_id": True, "continent_id": True, "trade_id": True, "country_code": True, "type": True, "display_name": True, "country": True, "default_params_required": True}}
      locations_response = maps.list_locations(obj)
      locations = []
      if 'list' in locations_response:
        locations = locations_response["list"]

      for location in locations:
        if str(self.location_id) == str(location['id']):
          self.location = self.get_required_location_data(location)
    
      return True


    def get_required_location_data(self, location):
        loc_data = {
          "id": location["id"],
          "name": location["name"],
          "is_icd": location["is_icd"],
          "port_code": location["port_code"],
          "country_id": location["country_id"],
          "continent_id": location["continent_id"],
          "trade_id": location["trade_id"],
          "country_code": location["country_code"],
          "type": location["type"],
          "display_name": location["display_name"],
          "country": location["country"]
        }
        return loc_data