from peewee import *
from database.db_session import db
import datetime
from playhouse.postgres_ext import *
from configs.env import DEFAULT_USER_ID


class BaseModel(Model):
    class Meta:
        database = db


class FclFreightRateLocalEstimationAudit(BaseModel):
    id = BigAutoField(primary_key=True, index=True)
    object_id = BigIntegerField(index=True)
    action_name = TextField()
    source = TextField()
    data = BinaryJSONField()
    performed_by_id = UUIDField(default=DEFAULT_USER_ID)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = "fcl_freight_rate_local_estimation_audits"

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(FclFreightRateLocalEstimationAudit, self).save(*args, **kwargs)