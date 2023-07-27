from peewee import *
from database.db_session import db
import datetime
from playhouse.postgres_ext import *

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class FclFreightLocationCluster(BaseModel):
    id = BigAutoField(primary_key=True)
    base_port_id = UUIDField(index=True)
    base_port = BinaryJSONField(null=True)
    trend_factor = DoubleField(default=1)
    map_zone_id = UUIDField(unique=True)
    status = CharField(index=True, default='active')
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    
    class Meta:
        table_name = 'fcl_freight_location_clusters'
    
    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(FclFreightLocationCluster, self).save(*args, **kwargs)
