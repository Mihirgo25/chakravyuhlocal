from peewee import *
from database.db_session import db
import datetime


class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class TrailerFreightRateCharges(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    country_code = CharField(index=True)
    currency_code = CharField()
    nh_toll = FloatField(null=True)
    tyre = FloatField(null=True)
    driver = FloatField(null=True)
    document = FloatField(null=True)
    handling = FloatField(null=True)
    maintanance = FloatField(null=True)
    misc = FloatField(null=True)
    status = CharField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = 'trailer_freight_rate_charges'

    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(TrailerFreightRateCharges, self).save(*args, **kwargs)