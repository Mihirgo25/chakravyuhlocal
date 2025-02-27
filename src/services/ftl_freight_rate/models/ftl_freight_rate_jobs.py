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

class FtlFreightRateJob(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    origin_location_id = UUIDField(null=False,index=True)
    origin_location = BinaryJSONField(null=True)
    destination_location_id = UUIDField(null=False,index=True)
    destination_location = BinaryJSONField(null=True)
    service_provider_id = UUIDField(null = True, index=True)
    service_provider = BinaryJSONField(null=True)
    truck_type = CharField(null=True,index = True)
    truck_body_type = CharField(null = True)
    trip_type = CharField(null = True)
    commodity= CharField(null=True)
    transit_time = TextField(null=True)
    detention_free_time = TextField(null=True)
    unit = CharField(null=True)
    sources = ArrayField(constraints=[SQL("DEFAULT '{}'::text[]")], field_class=TextField, null=True)
    user_id = UUIDField(index=True, null=True)
    assigned_to = BinaryJSONField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now, index=True)
    updated_at = DateTimeField(default=datetime.datetime.now, index=True)
    status = CharField(index=True, null=True)
    closed_by_id = UUIDField(null=True, index=True)
    closed_by = BinaryJSONField(null=True)
    closing_remarks = TextField(null=True)
    rate_type = TextField(null=True, index=True)
    is_visible = BooleanField(default=True)
    init_key = TextField(index=True, null=True)
    cogo_entity_id = UUIDField(null=True, index=True)
    serial_id = BigIntegerField(constraints=[SQL("DEFAULT nextval('ftl_freight_rate_jobs_serial_id_seq')")],)
    search_source = TextField(null=True, index=True)

    class Meta:
        table_name = 'ftl_freight_rate_jobs'

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(FtlFreightRateJob, self).save(*args, **kwargs)

    def set_locations(self):
      ids = [str(self.origin_location_id), str(self.destination_location_id)]    

      obj = {'filters':{"id": ids}, 'includes': {"id": True, "name": True, "is_icd": True, "port_code": True, "country_id": True, "continent_id": True, "trade_id": True, "country_code": True, "display_name": True, "country": True, "default_params_required": True}}
      locations_response = maps.list_locations(obj)
      locations = []
      if 'list' in locations_response:
        locations = locations_response["list"]

      for location in locations:
        if str(self.origin_location_id) == str(location['id']):
          self.origin_location = self.get_required_location_data(location)
        if str(self.destination_location_id) == str(location['id']):
          self.destination_location = self.get_required_location_data(location)

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
          "display_name": location["display_name"],
          "country": location.get("country")
        }
        return loc_data