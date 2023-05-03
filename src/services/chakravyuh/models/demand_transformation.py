from peewee import *
from database.db_session import db
import datetime
from playhouse.postgres_ext import *


class BaseModel(Model):
    class Meta:
        database = db


class DemandTransformation(BaseModel):
    id = BigAutoField(primary_key=True)
    origin_location_id = UUIDField(index=True, null=False)
    destination_location_id = UUIDField(index=True, null=False)
    origin_location_type = TextField(null=False, index=True)
    destination_location_type = TextField(null=False, index=True)
    service_type = TextField(index=True, null=False)
    customer_id = TextField(index=True, null=True)
    net_profit = FloatField(default=0)
    line_items = BinaryJSONField(default=[])
    date = DateTimeField(default=datetime.datetime.now().date())
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    status = TextField(default="active", null=False)

    class Meta:
        table_name = "demand_transformations"

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(DemandTransformation, self).save(*args, **kwargs)
