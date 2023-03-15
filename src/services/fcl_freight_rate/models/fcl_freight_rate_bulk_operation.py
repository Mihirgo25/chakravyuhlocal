from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
from configs.fcl_freight_rate_constants import TRADE_TYPES

class BaseModel(Model):
    class Meta:
        database = db

class FclFreightRateBulkOperation(BaseModel):
    action_name = CharField(null=True)
    created_at = DateTimeField()
    data = BinaryJSONField(null=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    performed_by_id = UUIDField(null=True)
    progress = IntegerField(constraints=[SQL("DEFAULT 0")], index=True, null=True)
    service_provider_id = UUIDField(null=True)
    updated_at = DateTimeField()

    class Meta:
        table_name = 'fcl_freight_rate_bulk_operations'
    
    