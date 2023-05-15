from peewee import *
from database.db_session import db
import uuid
import datetime


class BaseModel(Model):
    class Meta:
        database = db

class CountryBasicTrailerRate(Model):
    id = UUIDField(primary_key=True)
    country_code = CharField()
    container_size = CharField()
    commodity = CharField()
    rate_per_km = DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        table_name = 'country_basic_trailer_rates'

    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(CountryBasicTrailerRate, self).save(*args, **kwargs)