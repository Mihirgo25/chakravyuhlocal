from peewee import *
from database.db_session import db
import datetime
from playhouse.postgres_ext import *

class BaseModel(Model):
    class Meta:
        database = db

class FclRatePredictionFeedback(BaseModel):
    id = AutoField(primary_key=True)
    origin_port_id = TextField(index=True, null=True)
    destination_port_id = TextField(index = True, null=True)
    origin_country_id = TextField(null=True)
    destination_country_id = TextField(null=True)
    shipping_line_id = TextField(index = True, null=True)
    container_size = TextField(index = True, null=True)
    container_type = TextField(index = True, null=True)
    commodity = TextField(index = True, null=True)
    validity_start = DateTimeField(null=True)
    validity_end = DateTimeField(null=True)
    predicted_price = FloatField(null=True)
    actual_price = FloatField(null=True)
    predicted_price_currency = TextField(null=True)
    actual_price_currency = TextField(null=True)
    importer_exporter_id = UUIDField(null = True)
    source = TextField(null=True)
    creation_id = TextField(null = True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        db_table = "fcl_rate_prediction_feedbacks"
