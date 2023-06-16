from database.db_session import db
from peewee import * 
import json
from playhouse.postgres_ext import BinaryJSONField, ArrayField
from micro_services.client import *
from fastapi import HTTPException
from datetime import datetime,timedelta
ACTION_NAMES = ['delete_rate', 'add_markup']


class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class HaulageFreightRateBulkOperation(BaseModel):
    action_name = CharField(index = True, null=True)
    created_at = DateTimeField(default=datetime.now())
    data = BinaryJSONField(null=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    performed_by_id = UUIDField(null=True, index=True)
    performed_by = BinaryJSONField(null=True)
    sourced_by_id = UUIDField(null=True)
    sourced_by = BinaryJSONField(null=True)
    procured_by_id = UUIDField(null=True)
    procured_by = BinaryJSONField(null=True)
    progress = IntegerField(constraints=[SQL("DEFAULT 0")], index=True, null=True)
    service_provider_id = UUIDField(index=True, null=True)
    service_provider = BinaryJSONField(null=True)
    updated_at = DateTimeField(default=datetime.now())

    class Meta:
        table_name = 'haulage_freight_rate_bulk_operations'