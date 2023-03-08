from peewee import *
from database.db_session import db 
import datetime

class BaseModel(Model):
    class Meta:
        database = db
        
class FreightTrendPortPair(BaseModel):
    id = UUIDField(primary_key=True,constraints=[SQL("DEFAULT gen_random_uuid()")])
    origin_port_id = UUIDField(null=True)
    destination_port_id = UUIDField(null=True)
    last_updated_at = DateTimeField(null = True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)


    class Meta:
        table_name = 'freight_trend_port_pairs'
        # indexes = (("origin_port_id","destination_port_id"),False)
