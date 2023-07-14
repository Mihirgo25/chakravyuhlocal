from peewee import *
from database.db_session import db
import datetime
from playhouse.postgres_ext import ArrayField, DateTimeTZField
from services.haulage_freight_rate.models.haulage_freight_rate_rule_sets import HaulageFreightRateRuleSet


class BaseModel(Model):
    class Meta:
        database = db
class WagonTypes(BaseModel):
    id = BigAutoField(primary_key=True)
    wagon_type = CharField(index=True, null=True)
    wagon_code = CharField(index=True, null=True)
    name = CharField(index=True, null=True)
    permissible_speed = IntegerField(null=True)
    permissible_carrying_capacity = FloatField(null=True)
    commodity_allowed = ArrayField(CharField, null=True)
    loading_type = CharField(null=True)
    wagons_per_train =  IntegerField(null=True)
    cubic_capacity =  FloatField(null=True)
    container_size = CharField(null=True, index=True)
    unloading_type = CharField(null=True)
    remarks = CharField(null=True)
    status = CharField(index=True, default='active')
    created_at = DateTimeTZField(default=datetime.datetime.now, index=True)
    updated_at = DateTimeTZField(default=datetime.datetime.now, index=True)

    class Meta:
        table_name = 'wagon_types'

    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(WagonTypes, self).save(*args, **kwargs)
