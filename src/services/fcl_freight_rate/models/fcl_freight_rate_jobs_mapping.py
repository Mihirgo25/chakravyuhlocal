from peewee import *
import datetime
from database.db_session import db
from playhouse.postgres_ext import *
from fastapi import HTTPException
from params import Slab
from micro_services.client import *
from database.rails_db import *
from micro_services.client import maps
from services.fcl_freight_rate.models.fcl_freight_rate_jobs import FclFreightRateJobs


class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class FclFreightRateJobsMapping(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    source = TextField(index=True, null=True)
    source_id = UUIDField(index=True, null=True)
    job_id = ForeignKeyField(FclFreightRateJobs,to_field="id")
    created_at = DateField(default=datetime.datetime.now)
    updated_at = DateField(default=datetime.datetime.now)

    class Meta:
            table_name = 'fcl_freight_rate_jobs_mapping'

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(FclFreightRateJobsMapping, self).save(*args, **kwargs)
