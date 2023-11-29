from peewee import *
import datetime
from database.db_session import db
from services.fcl_freight_rate.models.fcl_freight_rate_local_job import FclFreightRateLocalJob


class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class FclFreightRateLocalJobMapping(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    source =  TextField(index=True)
    source_id = UUIDField(index=True, null=True)
    shipment_id = UUIDField(index=True, null=True)
    source_serial_id = BigIntegerField(index=True, null=True)
    shipment_service_id = UUIDField(index=True, null=True)
    status =  TextField(index=True, null=True)
    job_id = ForeignKeyField(FclFreightRateLocalJob,to_field="id")
    created_at = DateField(default=datetime.datetime.now)
    updated_at = DateField(default=datetime.datetime.now, index = True)

    class Meta:
            table_name = 'fcl_freight_rate_local_job_mappings'

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(FclFreightRateLocalJobMapping, self).save(*args, **kwargs)
