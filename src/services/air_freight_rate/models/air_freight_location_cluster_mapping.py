from peewee import *
from database.db_session import db
import datetime
from playhouse.postgres_ext import *

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class AirFreightLocationClusterMapping(BaseModel):
    id = BigAutoField(primary_key=True)
    location_id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    cluster_id = BigAutoField(ForeignKeyField)
    rate_factor = DoubleField(default=1)
    status = CharField(index=True, null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    
    class Meta:
        table_name = 'air_freight_location_cluster_mapping'
