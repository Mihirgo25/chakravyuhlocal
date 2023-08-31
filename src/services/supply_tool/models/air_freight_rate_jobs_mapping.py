from peewee import *
import datetime
from database.db_session import db
from playhouse.postgres_ext import *
from micro_services.client import *
from database.rails_db import *
from services.supply_tool.models.air_freight_rate_jobs import AirFreightRateJobs

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True
        
class AirFreightRateJobsMapping(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    source = TextField(index=True, null=True)
    source_id = UUIDField(index=True, null=True)
    job_id = ForeignKeyField(AirFreightRateJobs,to_field="id")
    performed_by_id = UUIDField(index=True, null=True)
    performed_by_type = TextField(index=True, null=True)
    created_at = DateField(default=datetime.datetime.now)
    updated_at = DateField(default=datetime.datetime.now)

    
    class Meta:
        table_name = 'air_freight_rate_jobs_mapping'

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(AirFreightRateJobsMapping, self).save(*args, **kwargs)