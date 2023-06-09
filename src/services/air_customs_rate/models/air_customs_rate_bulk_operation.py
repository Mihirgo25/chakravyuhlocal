from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
from datetime import datetime
from database.rails_db import *
from fastapi import HTTPException
from configs.global_constants import MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT
from micro_services.client import common
from services.fcl_customs_rate.interaction.list_fcl_customs_rates import list_fcl_customs_rates
from services.air_customs_rate.models.air_customs_rate_audit import AirCustomsRateAudit
from services.fcl_customs_rate.interaction.delete_fcl_customs_rate import delete_fcl_customs_rate
from services.fcl_customs_rate.interaction.update_fcl_customs_rate import update_fcl_customs_rate

ACTION_NAMES = ['delete_rate', 'add_markup']

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class AirCustomsRateBulkOperation(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    progress = IntegerField(constraints=[SQL("DEFAULT 0")], null=True)
    action_name = CharField(index = True, null=True)
    performed_by_id = UUIDField(null=True, index=True)
    created_at = DateTimeField(default=datetime.now())
    data = BinaryJSONField(null=True)
    updated_at = DateTimeField(default=datetime.now())
    service_provider_id = UUIDField(index=True, null=True)
    service_provider = BinaryJSONField(null=True)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super(AirCustomsRateBulkOperation, self).save(*args, **kwargs)

    class Meta:
        table_name = 'air_customs_rate_bulk_operations'