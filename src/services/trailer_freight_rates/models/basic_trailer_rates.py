from peewee import *
from database.db_session import db
import uuid
import datetime


class BaseModel(Model):
    class Meta:
        database = db

class BasicTrailerRate(BaseModel):
    base_rate = IntegerField(null=True)
    commodity = CharField(null=True, index=True)
    container_size = CharField(null=True, index=True)
    container_type = CharField(null=True, index=True)
    containers_count = IntegerField(null=True, )
    country_code = CharField(index=True)
    created_at = DateTimeField(default=datetime.datetime.now, index=True)
    currency = CharField(index=True)
    destination_location_id = UUIDField(null=True,index= True)
    distance = FloatField(index=True)
    id = UUIDField(
        primary_key=True,
        constraints=[SQL("DEFAULT uuid_generate_v4()")],
        default=uuid.uuid4,
    )
    origin_location_id = UUIDField(null=True,index= True)
    trailer_type = CharField(null=True)
    transit_time = IntegerField(null=True)
    weight = FloatField(null=True)
    status = CharField(default='active')
    updated_at = DateTimeField(default=datetime.datetime.now)
    

    class Meta:
        table_name = 'basic_trailer_rates'

    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(BasicTrailerRate, self).save(*args, **kwargs)