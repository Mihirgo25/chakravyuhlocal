from peewee import *
from database.db_session import db
import datetime
from playhouse.postgres_ext import *

class BaseModel(Model):
    class Meta:
        database = db

class FclRatePredictionFeedback(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    origin_port_id = UUIDField(index=True, null=True)
    destination_port_id = UUIDField(index = True, null=True)
    origin_main_port_id = UUIDField(null=True)
    destination_main_port_id = UUIDField(null=True)
    origin_country_id = UUIDField(null=True)
    destination_country_id = UUIDField(null=True)
    shipping_line_id = UUIDField(index = True, null=True)
    container_size = CharField(index = True, null=True)
    container_type = CharField(index = True, null=True)
    commodity = CharField(index = True, null=True)
    validity_start = DateTimeField(null=True)
    validity_end = DateTimeField(null=True)
    predicted_price = FloatField(null=True)
    actual_price = FloatField(null=True)
    predicted_price_currency = CharField(null=True)
    actual_price_currency = CharField(null=True)
    importer_exporter_id = UUIDField(null = True)
    source = CharField(null=True)
    creation_id = UUIDField(null = True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        db_table = "fcl_rate_prediction_feedbacks"
