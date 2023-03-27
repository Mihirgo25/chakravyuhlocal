from peewee import *
from database.db_session import db_cogo_lens
import datetime
from playhouse.postgres_ext import *

class BaseModel(Model):
    class Meta:
        database = db_cogo_lens

class FclRatePredictionFeedback(BaseModel):
    id = AutoField(primary_key=True)
    origin_port_id = TextField(null=True)
    destination_port_id = TextField(null=True)
    origin_country_id = TextField(null=True)
    destination_country_id = TextField(null=True)
    shipping_line_id = TextField(null=True)
    container_size = TextField(null=True)
    container_type = TextField(null=True)
    commodity = TextField(null=True)
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
        db_table = "fcl_rate_prediction_feedback"
        indexes = (
            (
                (
                    "origin_port_id",
                    "destination_port_id",
                    "origin_country_id",
                    "destination_country_id",
                    "shipping_line_id",
                    "container_size",
                    "container_type",
                    "commodity",
                ),
                False,
            ),
        )
