from peewee import *
from database.db_session import db
import datetime
from playhouse.postgres_ext import *
from configs.env import DEFAULT_USER_ID


class BaseModel(Model):
    class Meta:
        database = db


class CostBookingEstimationAudit(BaseModel):
    id = BigAutoField(primary_key=True, index=True)
    object_id = BigIntegerField(index=True)
    action_name = TextField()
    source = TextField()
    data = BinaryJSONField()
    performed_by_id = UUIDField(default=DEFAULT_USER_ID)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = "cost_booking_estimation_audits"

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(CostBookingEstimationAudit, self).save(*args, **kwargs)
