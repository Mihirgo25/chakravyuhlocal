from peewee import *
from database.db_session import db
import datetime
from playhouse.postgres_ext import *
from services.air_freight_rate.models.air_freight_location_clusters import AirFreightLocationClusters

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class AirFreightLocationClusterFactor(BaseModel):
    id = BigAutoField(primary_key=True)
    origin_cluster_id= ForeignKeyField(AirFreightLocationClusters,to_field="id")
    location_id=UUIDField(null=True,index=True)
    destination_cluster_id=ForeignKeyField(AirFreightLocationClusters,to_field="id")
    rate_factor=FloatField(default=1.0)
    

    class Meta:
        table_name='air_freight_location_cluster_factor'