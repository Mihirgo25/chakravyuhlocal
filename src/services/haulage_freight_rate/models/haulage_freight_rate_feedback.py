from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
import datetime
from configs.haulage_freight_rate_constants import FEEDBACK_SOURCES, POSSIBLE_FEEDBACKS, FEEDBACK_TYPES
from micro_services.client import *
from services.haulage_freight_rate.models.haulage_freight_rate import HaulageFreightRate
from database.rails_db import get_organization, get_user
from fastapi import HTTPException
import uuid

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True


class HaulageFreightRateFeedback(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    source = CharField(index=True, null=True)
    source_id = UUIDField(index=True, null=True)
    feedbacks = ArrayField(constraints=[SQL("DEFAULT '{}'::text[]")], field_class=TextField, null=True)
    remarks = ArrayField(constraints=[SQL("DEFAULT '{}'::text[]")], field_class=TextField, null=True)
    haulage_freight_rate_id = UUIDField(null=True,index=True)
    performed_by_id = UUIDField(index=True, null=True)
    performed_by = BinaryJSONField(null=True)
    performed_by_org_id = UUIDField(index=True, null=True)
    performed_by_org = BinaryJSONField(null=True)
    performed_by_type = CharField(index=True, null=True)
    preferred_freight_rate = DoubleField(null=True)
    preferred_freight_rate_currency = CharField(null=True)
    outcome = CharField(null=True)
    outcome_object_id = UUIDField(null=True)
    booking_params = BinaryJSONField(null=True)
    feedback_type = CharField(index=True, null=True)
    status = CharField(index=True, null=True)
    closing_remarks = ArrayField(constraints=[SQL("DEFAULT '{}'::text[]")], field_class=TextField, null=True)
    closed_by = BinaryJSONField(null=True)
    closed_by_id = UUIDField(index=True, null=True)
    serial_id = BigIntegerField(constraints=[SQL("DEFAULT nextval('haulage_freight_rate_feedback_serial_id_seq'::regclass)")])
    created_at = DateTimeTZField(index=True, default = datetime.datetime.now)
    updated_at = DateTimeTZField(default=datetime.datetime.now)
    origin_location_id = UUIDField(index=True,null=True)
    origin_city_id = UUIDField(null=True)
    origin_country_id = UUIDField(null=True)
    destination_location_id = UUIDField(index=True,null=True)
    destination_city_id = UUIDField(null=True)
    destination_country_id = UUIDField(null=True)
    commodity = CharField(null=True)
    container_size=CharField(null=True)
    container_type=CharField(null=True)
    service_provider_id= UUIDField(null=True)
    origin_location = BinaryJSONField(null=True)
    destination_location = BinaryJSONField(null=True)



    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(HaulageFreightRateFeedback, self).save(*args, **kwargs)

    class Meta:
        table_name = 'haulage_freight_rate_feedbacks'
    
    def validate_before_save(self):
        return True
        
    





