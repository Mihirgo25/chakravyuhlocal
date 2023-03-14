from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from peewee import *
from database.db_session import db
import datetime

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = db


class FclFreightRateMappings(BaseModel):
    created_at = DateTimeField(default=datetime.datetime.now)
    fcl_freight_id = ForeignKeyField(FclFreightRate, backref='fcl_freight_rate_mappings')
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    object_id = UUIDField(null=True)
    object_type = CharField(index=True, null=True)
    updated_at = DateTimeField(default=datetime.datetime.now)
    
    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(FclFreightRateMappings, self).save(*args, **kwargs)

    class Meta:
        table_name = 'fcl_freight_rate_mappings'
        indexes = (
            (('fcl_freight_id', 'object_type', 'object_id'), False),
            (('object_id', 'object_type'), False),
        )
