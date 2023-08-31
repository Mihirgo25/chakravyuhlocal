from peewee import *
import datetime
from database.db_session import db
from playhouse.postgres_ext import *
from fastapi import HTTPException
from params import Slab
from micro_services.client import *
from database.rails_db import *
from micro_services.client import maps


class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class FclFreightRateJobs(BaseModel):
        id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
        origin_port_id = UUIDField(index=True, null=True)
        origin_main_port_id = UUIDField(index=True, null=True)
        destination_port_id = UUIDField(index=True, null=True)
        destination_main_port_id = UUIDField(index=True, null=True)
        origin_port = BinaryJSONField(null=True)
        destination_port = BinaryJSONField(null=True)
        shipping_line_id = UUIDField(null=True, index=True)
        shipping_line = BinaryJSONField(null=True)
        service_provider_id = UUIDField(null=True, index=True)
        service_provider = BinaryJSONField(null=True)
        container_size = CharField(null=True, index=True)
        container_type = CharField(null=True, index=True)
        commodity = CharField(null=True, index=True)
        source = TextField(null=True, index = True)
        assigned_to_id = UUIDField(index=True, null=True)
        assigned_to = BinaryJSONField(null=True)
        created_at = DateTimeField(default=datetime.datetime.now)
        updated_at = DateTimeField(default=datetime.datetime.now)
        status = CharField(index=True, null=True)
        closed_by_id = UUIDField(null=True, index=True)
        closed_by = BinaryJSONField(null=True)
        closing_remarks = TextField(null=True)
        port = BinaryJSONField(null=True)
        port_id = UUIDField(null=True) #what logic
        rate_type = TextField(null=True)
        service_type = TextField(null=True)
        user_id = UUIDField(null=True)
        rate_id = UUIDField(null=True)

        class Meta:
            table_name = 'fcl_freight_rate_jobs'

        def save(self, *args, **kwargs):
            self.updated_at = datetime.datetime.now()
            return super(FclFreightRateJobs, self).save(*args, **kwargs)


