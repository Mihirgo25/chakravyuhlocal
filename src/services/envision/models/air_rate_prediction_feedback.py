from peewee import *
from database.db_session import db
import datetime
from playhouse.postgres_ext import *


class BaseModel(Model):
    class Meta:
        database = db


class AirFreightRatePredictionFeedback(BaseModel):
    id = AutoField(primary_key = True)
    origin_airport_id = TextField(null = True)
    destination_airport_id = TextField(null = True)
    airline_id = TextField(null = True)
    packages_count = IntegerField(null = True)
    volume = FloatField(null = True)
    weight = FloatField(null = True)
    date = DateTimeField(null = True)
    predicted_price = FloatField(null = True)
    actual_price = FloatField(null = True)
    predicted_price_currency = TextField(null = True)
    actual_price_currency = TextField(null = True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        db_table = "air_freight_rate_prediction_feedback"
