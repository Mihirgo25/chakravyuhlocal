from peewee import *
from database.db_session import db
import uuid
import datetime


class BaseModel(Model):
    class Meta:
        database = db

class TrailerFreightRateCharges(Model):
    id = UUIDField(primary_key=True)
    country_code = CharField()
    distance = FloatField(null=True)
    insurance = FloatField(null=True)
    toll = FloatField(null=True)
    driver = FloatField(null=True)
    document = FloatField(null=True)
    fuel = FloatField(null=True)
    handling = FloatField(null=True)
    food = FloatField(null=True)
    misc = FloatField(null=True)


    class Meta:
        table_name = 'country_basic_trailer_rates'

    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(TrailerFreightRateCharges, self).save(*args, **kwargs)