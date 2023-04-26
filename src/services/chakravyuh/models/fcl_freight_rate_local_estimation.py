from peewee import *
from database.db_session import db
from datetime import datetime
from playhouse.postgres_ext import *

class BaseModel(Model):
    class Meta:
        database = db
        
class FclFreightRateLocalEstimation(BaseModel):
    id = BigAutoField(primary_key=True)
    location_id = UUIDField(index=True, null=False)
    location_type = CharField(index=True, null=False)
    container_size = CharField(index=True, null=False)
    container_type = CharField(index=True, null=False)
    commodity = CharField(index=True)
    trade_type = CharField()
    shipping_line_id = UUIDField(index=True)
    line_items = BinaryJSONField(default = [])
    local_currency = CharField()
    status = CharField(default="active", null=False)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    
    class Meta:
        table_name = 'fcl_freight_rate_local_estimations'
        
    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super(FclFreightRateLocalEstimation, self).save(*args, **kwargs)