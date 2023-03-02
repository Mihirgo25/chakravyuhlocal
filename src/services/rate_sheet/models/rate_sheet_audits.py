from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
import datetime

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = db

class RateSheetAudits(BaseModel):
    id = UUIDField(
        primary_key=True,
        constraints=[SQL("DEFAULT uuid_generate_v4()")],
        default=uuid.uuid4,
        index=True
    )
    object_type = CharField(index=True, null=True)
    object_id = UUIDField(null=True)
    action_name = CharField(null=True)
    performed_by_id = UUIDField(index=True, null=True)
    data = JSONField(null=True)
    procured_by_id = UUIDField(index=True, null=True)
    sourced_by_id = UUIDField(index=True, null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = 'rate_sheet_audits'
