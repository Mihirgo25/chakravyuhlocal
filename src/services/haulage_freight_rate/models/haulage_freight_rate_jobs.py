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
        
class HaulageFreightRateJob(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    origin_location = BinaryJSONField(null=True)
    origin_location_id = UUIDField(null=True, index=True)
    destination_location = BinaryJSONField(null=True)
    destination_location_id = UUIDField(null=True, index=True)
    service_provider = BinaryJSONField(null=True)
    service_provider_id = UUIDField(null=True, index=True)
    shipping_line = BinaryJSONField(null=True)
    shipping_line_id = UUIDField(null=True, index=True)
    container_size = TextField(index=True, null=True)
    container_type = TextField(index=True, null=True)
    commodity = TextField(index=True, null=True)
    transport_modes_keyword = TextField(index=True, null=True)
    sources = ArrayField(constraints=[SQL("DEFAULT '{}'::text[]")], field_class=TextField, null=True)
    user_id = UUIDField(index=True, null=True)
    assigned_to = BinaryJSONField(null=True)
    closed_by_id = UUIDField(null=True, index=True)
    closed_by = BinaryJSONField(null=True)
    closing_remarks = TextField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now, index=True)
    status = CharField(index=True, null=True)
    rate_type = TextField(null=True)
    init_key = TextField(index=True, null=True)
    is_visible = BooleanField(default=True)
    cogo_entity_id = UUIDField(null=True, index=True)
    serial_id = BigIntegerField(constraints=[SQL("DEFAULT nextval('haulage_freight_rate_jobs_serial_id_seq')")],)
    source = TextField(default = 'manual',index=True, null = True)
    
    class Meta:
        table_name = 'haulage_freight_rate_jobs'
        
    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(HaulageFreightRateJob, self).save(*args, **kwargs)
    
    def set_locations(self):
      ids = [str(self.origin_location_id), str(self.destination_location_id)]
      
      obj = {'filters':{"id": ids, "type":'seaport'}, 'includes': {'id': True, 'name': True, 'type': True, 'is_icd': True, 'cluster_id': True, 'city_id': True, 'country_id':True, 'country_code': True, 'display_name': True, 'default_params_required': True}}
      locations_response = maps.list_locations(obj)
      locations = []
      if 'list' in locations_response:
        locations = locations_response["list"]

      for location in locations:
        if str(self.origin_location_id) == str(location['id']):
          self.origin_location = self.get_required_location_data(location)
        if str(self.destination_location_id) == str(location['id']):
          self.destination_location = self.get_required_location_data(location)
          
    def get_required_location_data(self, location):
        loc_data = {
          "id": location["id"],
          "name": location["name"],
          "is_icd": location["is_icd"],
          "type": location["type"],
          "cluster_id": location["cluster_id"],
          "city_id": location["city_id"],
          "country_id": location["country_id"],
          "country_code": location["country_code"],
          "display_name": location["display_name"]
        }
        return loc_data
      
    
    