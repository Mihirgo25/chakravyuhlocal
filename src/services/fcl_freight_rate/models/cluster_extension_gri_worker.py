from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
from micro_services.client import *
from database.rails_db import *
import datetime


class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class ClusterExtensionGriWorker(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    origin_port_id=UUIDField(index=True,null=True)
    origin_port=BinaryJSONField(null=True)
    destination_port=BinaryJSONField(null=True)
    destination_port_id=UUIDField(index=True,null=True)
    container_type = CharField(index=True, null=True)
    container_size = CharField(index=True, null=True)
    commodity= CharField(index=True, null=True)
    performed_by_id=UUIDField(index=True,null=True)
    performed_by=BinaryJSONField(null=True)
    min_decrease_amount =FloatField(index=True,null=True)
    max_increase_amount = FloatField(index=True,null=True)
    min_decrease_percent =FloatField(index=True,null=True)
    max_increase_percent = FloatField(index=True,null=True)
    manual_gri=FloatField(index=True,null=True)
    approval_status=CharField(index=True, null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = 'cluster_extension_gri_worker'

 
    def set_locations(self):
      ids = [str(self.origin_port_id), str(self.destination_port_id)]

      obj = {'filters':{"id": ids}}
      locations_response = maps.list_locations(obj)

      locations = []
      if 'list' in locations_response:
        locations = locations_response["list"]

      for location in locations:
        if str(self.origin_port_id) == str(location['id']):
          self.origin_port = self.get_required_location_data(location)
        if str(self.destination_port_id) == str(location['id']):
          self.destination_port = self.get_required_location_data(location)



    def get_required_location_data(self, location):
        loc_data = {
            "id": location["id"],
            "name": location["name"],
            "display_name": location["display_name"]
        }
        return loc_data 