from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
import datetime

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = db

class RateSheet(BaseModel):
    id = UUIDField(
        primary_key=True,
        constraints=[SQL("DEFAULT uuid_generate_v4()")],
        default=uuid.uuid4,
    )
    service_provider_id = UUIDField(index=True, null=True)
    service_name = CharField(null=True)
    file_url = CharField(null=True)
    comment = CharField(null=True)
    status = CharField(null=True)
    converted_files = JSONField(null=True)
    partner_id = UUIDField(index=True, null=True)
    agent_id = UUIDField(index=True, null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    serial_id = IntegerField(null=True)
    cogo_entity_id = UUIDField(index=True, null=True)

    class Meta:
        table_name = 'rate_sheet'
