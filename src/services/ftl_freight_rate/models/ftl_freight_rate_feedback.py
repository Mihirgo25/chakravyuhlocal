from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
from services.ftl_freight_rate.models.ftl_freight_rate import FtlFreightRate
from fastapi import HTTPException
import datetime
from database.rails_db import *
from micro_services.client import common, maps, spot_search


class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class FtlFreightRateFeedback(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    source = CharField(index=True, null=True)
    source_id = UUIDField(index=True, null=True)
    feedbacks = ArrayField(constraints=[SQL("DEFAULT '{}'::text[]")], field_class=TextField, null=True)
    remarks = ArrayField(constraints=[SQL("DEFAULT '{}'::text[]")], field_class=TextField, null=True)
    ftl_freight_rate_id = UUIDField(null=True,index=True)
    performed_by_id = UUIDField(index=True, null=True)
    performed_by_org_id = UUIDField(index=True, null=True)
    performed_by_type = CharField(index=True, null=True)
    preferred_freight_rate = DoubleField(null=True)
    preferred_freight_rate_currency = CharField(null=True)
    outcome = CharField(null=True)
    outcome_object_id = UUIDField(null=True)
    booking_params = BinaryJSONField(null=True)
    feedback_type = CharField(index=True, null=True)
    status = CharField(index=True, null=True)
    created_at = DateTimeTZField(index=True, default = datetime.datetime.now)
    updated_at = DateTimeTZField(default=datetime.datetime.now)
    closing_remarks = ArrayField(constraints=[SQL("DEFAULT '{}'::text[]")], field_class=TextField, null=True)
    serial_id = BigIntegerField(constraints=[SQL("DEFAULT nextval('fcl_freight_rate_feedback_serial_id_seq'::regclass)")])
    closed_by_id = UUIDField(index=True, null=True)
    origin_location_id = UUIDField(index=True,null=True)
    origin_country_id = UUIDField(null=True)
    destination_location_id = UUIDField(index=True,null=True)
    destination_country_id = UUIDField(null=True)
    service_provider_id= UUIDField(null=True)

    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(FtlFreightRateFeedback, self).save(*args, **kwargs)

    class Meta:
        table_name = 'ftl_freight_rate_feedbacks'



