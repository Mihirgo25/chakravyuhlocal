from peewee import * 
from database.db_session import db
from playhouse.postgres_ext import *
from services.fcl_freight_rate.models.fcl_freight_rates import FclFreightRate
import datetime

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = db

class FclFreightRateAudit(BaseModel):
    action_name = CharField(null=True)
    bulk_operation_id = UUIDField(index=True, null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    data = BinaryJSONField(null=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    object_id = UUIDField(null=True)
    object_type = CharField(null=True)
    performed_by_id = UUIDField(null=True)
    procured_by_id = UUIDField(null=True)
    rate_sheet_id = UUIDField(index=True, null=True)
    source = CharField(null=True)
    sourced_by_id = UUIDField(null=True)
    updated_at = DateTimeField(default=datetime.datetime.now)
    object_id = ForeignKeyField(FclFreightRate, related_name='audits', on_delete='CASCADE')
    seqnum = Window(
        partition_by = object_id,
        order_by = created_at.desc()
    )

    class Meta:
        database = db

    class Meta:
        table_name = 'fcl_freight_rate_audits'
        indexes = (
            (('object_type', 'object_id'), False),
        )