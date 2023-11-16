from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
from fastapi import HTTPException
from services.air_freight_rate.constants.air_freight_rate_constants import *
from micro_services.client import *
from database.rails_db import *
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
import datetime
from fastapi.encoders import jsonable_encoder

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class AirFreightRateLocalFeedback(BaseModel):
    air_freight_rate_local_id = UUIDField(null=True,index=True)
    booking_params = BinaryJSONField(null=True)
    closed_by_id = UUIDField(null=True,index=True)
    closing_remarks = ArrayField(
        constraints=[SQL("DEFAULT '{}'::character varying[]")],
        field_class=TextField,
        null=True,
    )
    created_at = DateTimeField(default=datetime.datetime.now)
    feedback_type = CharField(null=True)
    feedbacks = ArrayField(field_class=TextField, null=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    performed_by_id = UUIDField(null=True,index=True)
    performed_by = BinaryJSONField(null=True)
    performed_by_org_id = UUIDField(null=True,index=True)
    performed_by_org = BinaryJSONField(null=True)
    performed_by_type = CharField(null=True)
    # preferred_airline_ids = ArrayField(field_class=UUIDField, null=True)
    # preferred_airlines = BinaryJSONField(null=True)
    preferred_rate = DoubleField(null=True)
    preferred_rate_currency = CharField(null=True)
    preferred_storage_free_days = IntegerField(null=True)
    remarks = ArrayField(field_class=TextField, null=True)
    serial_id = BigIntegerField(
        constraints=[
            SQL("DEFAULT nextval('air_freight_rate_local_feedback_serial_id_seq'::regclass)")
        ]
    )
    source = CharField(null=True)
    source_id = UUIDField(null=True,index=True)
    status = CharField(null=True)
    trade_type = CharField(null=True)
    updated_at = DateTimeField(default=datetime.datetime.now)
    closed_by = BinaryJSONField(null=True)
    reverted_rate= BinaryJSONField(null=True)
    airport_id = UUIDField(null=True, index=True)
    country_id = UUIDField(null=True, index=True)
    continent_id = UUIDField(null=True, index=True)
    trade_id = UUIDField(null=True, index=True)
    cogo_entity_id = UUIDField(null=True, index=True)
    service_provider_id = UUIDField(null=True, index=True)
    commodity = TextField(null=True,index=True)
    operation_type = TextField(null=True,index=True)
    airline_id=UUIDField(null=True,index=True)
    spot_search_serial_id = BigIntegerField(null = True)

    class Meta:
        table_name = "air_freight_rate_local_feedbacks"
    
    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(AirFreightRateLocalFeedback, self).save(*args, **kwargs)