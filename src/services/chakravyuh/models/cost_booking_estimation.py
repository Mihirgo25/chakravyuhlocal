from peewee import *
from database.db_session import db
import datetime
from playhouse.postgres_ext import *
from micro_services.client import common, maps
from services.chakravyuh.models.cost_booking_estimation_audit import CostBookingEstimationAudit
class BaseModel(Model):
    class Meta:
        database = db
class CostBookingEstimation(BaseModel):
    id = BigAutoField(primary_key=True)
    origin_location_id = UUIDField(index=True, null=False)
    origin_location_type = CharField(null=False, index=True)
    destination_location_id = UUIDField(index=True, null=False)
    destination_location_type = CharField(null=False, index=True)
    shipping_line_id = UUIDField(null=True, index=True)
    container_size = CharField(null=False, index=True)
    container_type = CharField(null=False, index=True)
    commodity = CharField(null=True)
    schedule_type = CharField(null=True)
    payment_term = CharField(null=True)
    line_items = BinaryJSONField(default=[])
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    status = CharField(default="active", null=False)
    origin_location = BinaryJSONField(null=True)
    destination_location = BinaryJSONField(null=True)
    shipping_line = BinaryJSONField(null=True)

    class Meta:
        table_name = "cost_booking_estimations"
        indexes = ((('origin_location_id', 'destination_location_id', 'container_size', 'container_type', 'commodity', 'shipping_line_id'), True),)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(CostBookingEstimation, self).save(*args, **kwargs)
    

    def set_attribute_objects(self):
        from database.rails_db import get_shipping_line
        location_ids = [str(self.origin_location_id), str(self.destination_location_id)]

        locations_response = maps.list_locations({ 'filters': { 'id': location_ids }})

        if 'list' in locations_response:
            locations_list = locations_response['list']
            for location in locations_list:
                if location['id'] == str(self.origin_location_id):
                    self.origin_location = location
                if location['id'] == str(self.destination_location_id):
                    self.destination_location = location
        if self.shipping_line_id:
            shipping_line_list = get_shipping_line(str(self.shipping_line_id))

            if shipping_line_list:
                self.shipping_line = shipping_line_list[0]
        
        self.save()
    
                    
    def create_audit(self, param):
        audit = CostBookingEstimationAudit.create(**param)
        return audit