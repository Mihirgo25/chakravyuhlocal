from peewee import *
from database.db_session import db
import datetime
from playhouse.postgres_ext import *

class BaseModel(Model):
    class Meta:
        database = db
        
class RevenueTargetAudit(BaseModel):
    id = BigAutoField(primary_key=True)
    object_id = BigIntegerField(index=True)
    action_name = CharField()
    source = CharField()
    data = BinaryJSONField()
    performed_by_id = UUIDField(index=True)
    created_at = DateTimeField(default=datetime.datetime.now, index=True)
    updated_at = DateTimeField(default=datetime.datetime.now)
    
    class Meta:
        table_name = "revenue_target_audits"

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(RevenueTargetAudit, self).save(*args, **kwargs)