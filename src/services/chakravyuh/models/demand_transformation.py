from peewee import *
from database.db_session import db
import datetime
from playhouse.postgres_ext import *
from services.chakravyuh.models.demand_transformation_audit import DemandTransformationAudit


class BaseModel(Model):
    class Meta:
        database = db


class DemandTransformation(BaseModel):
    id = BigAutoField(primary_key=True)
    origin_location_id = UUIDField(index=True, null=False)
    destination_location_id = UUIDField(index=True, null=False)
    origin_location_type = TextField(null=False, index=True)
    destination_location_type = TextField(null=False, index=True)
    service_type = TextField(index=True, null=False)
    customer_id = TextField(index=True, null=True)
    net_profit = FloatField(default=0)
    line_items = BinaryJSONField(default=[])
    date = DateTimeField(default=datetime.datetime.now().date())
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    realised_volume = IntegerField(default=0)
    realised_revenue = FloatField(default=0)
    realised_currency = CharField(default='USD')
    status = CharField(default="active", null=False)

    class Meta:
        table_name = "demand_transformations"

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(DemandTransformation, self).save(*args, **kwargs)
    
    def create_audit(self, param):
        audit = DemandTransformationAudit.create(**param)
        return audit
