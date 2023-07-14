from peewee import *
from database.db_session import db
from datetime import datetime
from playhouse.postgres_ext import *
from services.fcl_freight_rate.models.fcl_freight_location_cluster import FclFreightLocationCluster

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class FclFreightLocationClusterFactor(BaseModel):
    id = BigAutoField(primary_key=True)
    location_id = UUIDField(null=True, index=True)
    container_size = CharField(null=True, index=True)
    container_type = CharField(null=True, index=True)
    shipping_line_id = UUIDField(null=True, index=True)
    cluster_id = ForeignKeyField(FclFreightLocationCluster, to_field="id")
    origin_cluster_id = ForeignKeyField(FclFreightLocationCluster, to_field="id")
    destination_cluster_id = ForeignKeyField(FclFreightLocationCluster, to_field="id")
    rate_factor = FloatField(default=1)
    trend_factor = DoubleField(default=1)
    status = CharField(default='active', index=True)
    created_at = DateTimeField(default=datetime.now())
    update_at = DateTimeField(default=datetime.now())

    class Meta:
        table_name='fcl_freight_location_cluster_factors'
        indexes = (
        (("origin_cluster_id", "location_id","destination_cluster_id","cluster_id"), True),)
        
    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(FclFreightLocationClusterFactor, self).save(*args, **kwargs)