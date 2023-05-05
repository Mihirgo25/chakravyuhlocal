from peewee import *
from database.db_session import db
import uuid
import datetime


class BaseModel(Model):
    class Meta:
        database = db
class RailRatesIndia(BaseModel):
    id = UUIDField(
        primary_key=True,
        constraints=[SQL("DEFAULT uuid_generate_v4()")],
        default=uuid.uuid4,
    )
    distance = FloatField(index=True)
    load_type = CharField(index=True)
    class_type = CharField(index=True)
    base_rate = IntegerField()
    created_at = DateTimeField(default=datetime.datetime.now, index=True)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = 'rail_rates_india'

    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(RailRatesIndia, self).save(*args, **kwargs)
