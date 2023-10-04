from peewee import *
import datetime
from database.db_session import db
from playhouse.postgres_ext import *
from micro_services.client import *
from database.rails_db import *

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True


class AirCustomsRateJob(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    airport_id = UUIDField(index=True, null= True)
    airport = BinaryJSONField(null=True)
    country_id = UUIDField(index=True, null= True)
    service_provider = BinaryJSONField(null=True)
    service_provider_id = UUIDField(null=True, index=True)
    commodity = CharField(null=True, index=True)
    created_at = DateTimeField(default=datetime.datetime.now, index=True)
    updated_at = DateTimeField(default=datetime.datetime.now, index=True)
    status = CharField(index=True, null=True)
    sources = ArrayField(constraints=[SQL("DEFAULT '{}'::text[]")], field_class=TextField, null=True)
    user_id = UUIDField(index=True, null=True)
    assigned_to = BinaryJSONField(null=True)
    closed_by_id = UUIDField(null=True, index=True)
    closed_by = BinaryJSONField(null=True)
    closing_remarks = TextField(null=True)
    shipment_type = CharField(null=True)
    stacking_type = CharField(null=True, index=True)
    rate_type = TextField(null=True)
    init_key = TextField(index=True, null=True)
    commodity_type = CharField(null=True)
    commodity_sub_type = CharField(null=True)
    operation_type = CharField(null=True)
    price_type = CharField(null=True)
    is_visible = BooleanField(default=True)
    cogo_entity_id = UUIDField(null=True, index=True)
    serial_id = BigIntegerField(constraints=[SQL("DEFAULT nextval('air_customs_rate_jobs_serial_id_seq')")],)
    mode = CharField(default = 'manual', index = True, null = True)

    class Meta:
        table_name = 'air_customs_rate_jobs'

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(AirCustomsRateJob, self).save(*args, **kwargs)

    def set_locations(self):

      ids = self.airport_id

      obj = {'filters':{"id": ids, "type":'airport'}}
      locations_response = maps.list_locations(obj)
      locations = []
      if 'list' in locations_response:
        locations = locations_response["list"]

      for location in locations:
        if str(self.airport_id) == str(location['id']):
          self.airport = self.get_required_location_data(location)
          self.country_id = self.airport.get("country_id")
        
    def get_required_location_data(self, location):
        loc_data = {
          "id": location["id"],
          "type":location['type'],
          "name":location['name'],
          "display_name": location["display_name"],
          "is_icd": location["is_icd"],
          "port_code": location["port_code"],
          "country_id": location["country_id"],
          "continent_id": location["continent_id"],
          "trade_id": location["trade_id"],
          "country_code": location["country_code"]
        }
        return loc_data
