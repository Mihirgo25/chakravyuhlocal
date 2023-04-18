from peewee import *
from database.db_session import db
import datetime
from playhouse.postgres_ext import *

class BaseModel(Model):
    class Meta:
        database = db

class FclFreightRateEstimation(BaseModel):
    id = BigAutoField(primary_key=True)
    origin_location_id = UUIDField(index=True,null=False)
    destination_location_id = UUIDField(index=True,null=False)
    origin_location_type = TextField(null=True,index=True)
    destination_location_type = TextField(null=True,index=True)
    shipping_line_id = UUIDField(null=True,index=True)
    container_size = TextField(null=True,index= True)
    container_type = TextField(null=True,index= True)
    commodity = TextField(null=True)
    lower_rate = FloatField(null=False)
    upper_rate = FloatField(null=False)
    currency = TextField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    status = TextField(default='active',null=False)

    class Meta:
        table_name = 'fcl_freight_rate_estimation'

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(FclFreightRateEstimation, self).save(*args, **kwargs)
    
    


