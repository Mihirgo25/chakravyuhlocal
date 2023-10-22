from peewee import *
import datetime
from database.db_session import db
from playhouse.postgres_ext import *
from fastapi import HTTPException
from params import Slab
from micro_services.client import *
from database.rails_db import *
from micro_services.client import maps
from services.fcl_customs_rate.models.fcl_customs_rate_jobs import FclCustomsRateJob


class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class FclCustomsRateJobMapping(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    source =  TextField(index=True)
    source_id = UUIDField(index=True, null=True)
    shipment_id = UUIDField(index=True, null=True)
    shipment_serial_id = BigIntegerField(index=True, null=True)
    shipment_service_id = UUIDField(index=True, null=True)
    status = CharField(index=True, null=True)
    job_id = ForeignKeyField(FclCustomsRateJob,to_field="id")
    created_at = DateField(default=datetime.datetime.now)
    updated_at = DateField(default=datetime.datetime.now, index = True)

    class Meta:
            table_name = 'fcl_customs_rate_job_mappings'

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(FclCustomsRateJobMapping, self).save(*args, **kwargs)