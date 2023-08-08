from peewee import *
from database.db_session import db
import datetime
from playhouse.postgres_ext import *
from micro_services.client import common, maps
from services.chakravyuh.models.air_freight_rate_estimation_audit import AirFreightRateEstimationAudit

class BaseModel(Model):
    class Meta:
        database = db

class AirFreightRateEstimation(BaseModel):
    id = BigAutoField(primary_key=True)
    origin_location_id = UUIDField(index=True, null=False)
    origin_location_type = CharField(null=False, index=True)
    destination_location_id = UUIDField(index=True, null=False)
    destination_location_type = CharField(null=False, index=True)
    airline_id = UUIDField(null=True, index=True)
    commodity = CharField(null=False)
    operation_type = TextField(null=False)
    weight_slabs = BinaryJSONField(default=[])
    stacking_type = TextField(null=True)
    shipment_type = TextField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    status = CharField(default="active", null=False)
    origin_location = BinaryJSONField(null=True)
    destination_location = BinaryJSONField(null=True)
    airline = BinaryJSONField(null=True)

    class Meta:
        table_name = "air_freight_rate_estimations"

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(AirFreightRateEstimation, self).save(*args, **kwargs)
    
    def set_attribute_objects(self):
        from database.rails_db import get_operators
        location_ids = [str(self.origin_location_id), str(self.destination_location_id)]

        locations_response = maps.list_locations({ 'filters': { 'id': location_ids }})

        if 'list' in locations_response:
            locations_list = locations_response['list']
            for location in locations_list:
                if location['id'] == str(self.origin_location_id):
                    self.origin_location = location
                if location['id'] == str(self.destination_location_id):
                    self.destination_location = location
        if self.airline_id:
            airline_list = get_operators(str(self.airline_id))

            if airline_list:
                self.airline = airline_list[0]
        
        self.save()
                           
    def create_audit(self, param):
        audit = AirFreightRateEstimationAudit.create(**param)
        return audit