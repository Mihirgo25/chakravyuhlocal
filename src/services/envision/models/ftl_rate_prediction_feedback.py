from peewee import *
from database.db_session import db
import datetime
from playhouse.postgres_ext import *


class BaseModel(Model):
    class Meta:
        database = db


class FtlRatePredictionFeedback(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    origin_location_id = TextField(index=True, null=True)
    destination_location_id = TextField(index=True, null=True)
    origin_region_id = TextField(index=True, null=True)
    destination_region_id = TextField(index=True, null=True)
    truck_type = TextField(index=True, null=True)
    transit_time = TextField(null=True)
    validity_start = DateTimeField(null=True)
    validity_end = DateTimeField(null=True)
    predicted_price = FloatField(null=True)
    actual_price = FloatField(null=True)
    predicted_price_currency = TextField(null=True)
    actual_price_currency = TextField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        db_table = "ftl_rate_prediction_feedbacks"
