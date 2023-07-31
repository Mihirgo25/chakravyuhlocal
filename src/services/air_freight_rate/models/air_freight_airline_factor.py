from peewee import *
from database.db_session import db
import datetime
from playhouse.postgres_ext import *
from services.air_freight_rate.models.air_freight_location_cluster import AirFreightLocationCluster
class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class AirFreightAirlineFactor(BaseModel):
    id = BigAutoField(primary_key=True)
    base_airline_id = UUIDField(index=True)
    derive_airline_id = UUIDField(index=True)
    status = CharField(index=True, default='active')
    origin_cluster_id = ForeignKeyField(AirFreightLocationCluster,to_field="id")
    destination_cluster_id = ForeignKeyField(AirFreightLocationCluster,to_field= "id")
    origin_airport_id = UUIDField(index=True)
    destination_airport_id = UUIDField(index=True)
    slab_wise_factor = BinaryJSONField()    
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    
    class Meta:
        table_name = 'air_freight_airline_factors'
        indexes = (
        (("origin_airport_id","destination_airport_id","derive_airline_id","base_airline_id"), True),)