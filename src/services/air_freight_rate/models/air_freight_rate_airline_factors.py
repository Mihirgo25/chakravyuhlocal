from peewee import *
from database.db_session import db
import datetime
from playhouse.postgres_ext import *
from services.air_freight_rate.models.air_freight_location_clusters import AirFreightLocationClusters
class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class AirFreightLocationClusters(BaseModel):
    id = BigAutoField(primary_key=True)
    base_airline_id = UUIDField(index=True)
    derive_airline_id = UUIDField(index=True)
    status = CharField(index=True, default='active')
    origin_cluster_id = ForeignKeyField(AirFreightLocationClusters,to_field="id")
    destination_cluster_id = ForeignKeyField(AirFreightLocationClusters,to_field= "id")
    rate_factor = DoubleField(default=1)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    
    class Meta:
        table_name = 'air_freight_location_clusters'