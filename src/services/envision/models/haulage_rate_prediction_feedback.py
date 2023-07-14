from peewee import *
from database.db_session import db
import datetime
from playhouse.postgres_ext import *


class BaseModel(Model):
    class Meta:
        database = db


class HaulageRatePredictionFeedback(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    origin_location_id = TextField(index=True, null=True)
    destination_location_id = TextField(index=True, null=True)
    container_size = TextField(index=True, null=True)
    container_type = TextField(index=True, null=True)
    lower_limit = FloatField(null=True)
    upper_limit = FloatField(null=True)
    commodity = TextField(index=True, null=True)
    service_provider_id = TextField(index=True, null=True)
    transport_modes = ArrayField(field_class=TextField, null=True, index=True)
    haulage_type = TextField(index=True, null=True)
    transit_time = TextField(null=True)
    detention_free_time = TextField(null=True)
    validity_start = DateTimeTZField(null=True)
    validity_end = DateTimeTZField(null=True)
    predicted_price = FloatField(null=True)
    actual_price = FloatField(null=True)
    predicted_price_currency = TextField(null=True)
    actual_price_currency = TextField(null=True)
    created_at = DateTimeTZField(default=datetime.datetime.now)
    updated_at = DateTimeTZField(default=datetime.datetime.now)

    class Meta:
        db_table = "haulage_rate_prediction_feedbacks"