from peewee import *
from database.db_session import db
import datetime
from playhouse.postgres_ext import *
from services.chakravyuh.models.revenue_target_audit import RevenueTargetAudit

class BaseModel(Model):
    class Meta:
        database = db
        
class RevenueTarget(BaseModel):
    id = BigAutoField(primary_key=True)
    origin_location_id = UUIDField(index=True, null=False)
    origin_location_type = CharField(null=False, index=True)
    destination_location_id = UUIDField(index=True, null=False)
    destination_location_type = CharField(null=False, index=True)
    service_type = CharField(index=True, null=False)
    customer_id = TextField(index=True, null=True)
    total_loss = FloatField(default=0)
    date = DateTimeField(default=datetime.datetime.now().date())
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    total_volume = IntegerField(default=0)
    total_revenue = FloatField(default=0)
    total_currency = CharField(default='USD')
    status = CharField(default="active", null=False)

    class Meta:
        table_name = "revenue_targets"

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(RevenueTarget, self).save(*args, **kwargs)
    
    def create_audit(self, param):
        audit = RevenueTargetAudit.create(**param)