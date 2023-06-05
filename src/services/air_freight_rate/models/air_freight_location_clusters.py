from peewee import *
from database.db_session import db
import datetime
from playhouse.postgres_ext import *

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class AirFreightLocationClusters(BaseModel):
    id = BigAutoField(primary_key=True)
    base_airport_id = UUIDField(index=True)
    base_airport = BinaryJSONField(null=True)
    status = CharField(index=True, null=True)
    trend_factor = DoubleField(default=1)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    
    class Meta:
        table_name = 'air_freight_location_clusters'
