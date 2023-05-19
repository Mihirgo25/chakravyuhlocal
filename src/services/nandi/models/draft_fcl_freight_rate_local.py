from peewee import * 
from database.db_session import db
from playhouse.postgres_ext import *
import datetime
from micro_services.client import *

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True
        
class DraftFclFreightRateLocal(BaseModel):
    commodity = CharField(index=True, null=True)
    container_size = CharField(index=True, null=True)
    container_type = CharField(index=True, null=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    rate_id = UUIDField(index=True, null=False)
    data = BinaryJSONField(constraints=[SQL("DEFAULT '{}'::jsonb")], null=True)
    source = CharField(null=False)
    status = CharField(null=False)
    invoice_url = TextField(null=True, index=True)
    invoice_date = DateField(null=True)
    main_port = BinaryJSONField(null=True)
    main_port_id = UUIDField( null=True)
    port = BinaryJSONField(null=True)
    port_id = UUIDField(index=True, null=True)
    shipment_serial_id = BigIntegerField(null=True, index= False)
    shipping_line = BinaryJSONField(null=True)
    shipping_line_id = UUIDField(index=True, null=True)
    trade_type = CharField(index=True, null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now, index=True)
    
    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(DraftFclFreightRateLocal, self).save(*args, **kwargs)

    class Meta:
        table_name = 'draft_fcl_freight_rate_locals'

    def set_main_port(self):
        if self.main_port_id:
          obj = {'filters':{"id": self.main_port_id, "type":'seaport'}}
          locations_response = maps.list_locations(obj)
          if 'list' in locations_response and len(locations_response['list']) > 0:
              location_data = locations_response['list'][0]
              self.main_port = self.get_required_location_data(location_data)
            
    def get_required_location_data(self, location):
        loc_data = {
          "id": location["id"],
          "name": location["name"],
          "is_icd": location["is_icd"],
          "port_code": location["port_code"],
          "country_id": location["country_id"],
          "continent_id": location["continent_id"],
          "trade_id": location["trade_id"],
          "country_code": location["country_code"]
        }
        return loc_data