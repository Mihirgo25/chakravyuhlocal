from peewee import *
from database.db_session import db
import datetime
from playhouse.postgres_ext import *
from services.fcl_freight_rate.models.fcl_freight_location_cluster import FclFreightLocationCluster

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class FclFreightLocationClusterMapping(BaseModel):
    id = BigAutoField(primary_key=True)
    location_id = UUIDField(index=True,unique=True)
    cluster_id = ForeignKeyField(FclFreightLocationCluster,to_field="id")
    status = CharField(index=True, default='active')
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    
    class Meta:
        table_name = 'fcl_freight_location_cluster_mappings'
        
    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(FclFreightLocationClusterMapping, self).save(*args, **kwargs)
