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
        indexes = ((('origin_location_id', 'destination_location_id', 'container_size', 'container_type'), True),)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(CostBookingEstimation, self).save(*args, **kwargs)
    
                    
    def create_audit(self, param):
        audit = CostBookingEstimationAudit.create(**param)
        return audit