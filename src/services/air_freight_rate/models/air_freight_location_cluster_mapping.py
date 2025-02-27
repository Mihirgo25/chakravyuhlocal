from peewee import *
from database.db_session import db
import datetime
from playhouse.postgres_ext import *
from services.air_freight_rate.models.air_freight_location_cluster import AirFreightLocationCluster

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class AirFreightLocationClusterMapping(BaseModel):
    id = BigAutoField(primary_key=True)
    location_id = UUIDField(index=True,unique=True)
    cluster_id = ForeignKeyField(AirFreightLocationCluster,to_field="id")
    status = CharField(index=True, default='active')
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    
    class Meta:
        table_name = 'air_freight_location_cluster_mappings'
