from peewee import *
import datetime
from database.db_session import db
from services.air_freight_rate.models.air_freight_rate import AirFreightRate


class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class AirFreightRateProperty(BaseModel):
    id = BigAutoField(primary_key=True)
    bookings_count = IntegerField(null=True)
    bookings_importer_exporters_count = IntegerField(null=True)
    priority_score = IntegerField(null=True)
    priority_score_updated_at = DateTimeField(default=datetime.datetime.now, index=True)
    spot_searches_count = IntegerField(null=True)
    spot_searches_importer_exporters_count = IntegerField(null=True)
    created_at = DateField(default=datetime.datetime.now())
    updated_at = DateField(default=datetime.datetime.now())
    air_freight_rate_id = ForeignKeyField(AirFreightRate, backref='air_freight_rate_property', null=True)

    class Meta:
        db_table = "air_freight_rate_properties"