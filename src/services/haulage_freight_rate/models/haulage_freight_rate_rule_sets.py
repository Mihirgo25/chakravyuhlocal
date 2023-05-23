from peewee import *
from database.db_session import db
import uuid
import datetime
from playhouse.postgres_ext import BinaryJSONField


class BaseModel(Model):
    class Meta:
        database = db
class HaulageFreightRateRuleSet(BaseModel):
    id = BigAutoField(primary_key=True)
    distance = FloatField(index=True)
    wagon_count = IntegerField(index=True, null=True)
    status = CharField(index=True, default='active')
    train_load_type = CharField(index=True)
    commodity_class_type = CharField(index=True)
    commodity_type = CharField(index=True, null=True)
    wagon_type = CharField(index=True, null=True)
    base_price = DecimalField(max_digits=20, decimal_places=5)
    running_base_price = DecimalField(null=True, max_digits=20, decimal_places=5)
    base_price_unit =  CharField(index=True, null=True)
    running_base_price_unit = CharField(index=True, null=True)
    container_type =  CharField(index=True, null=True)
    base_rate_unit = CharField(index=True, null=True)
    country_code = CharField(index=True)
    currency = CharField(index=True)
    transit_time = IntegerField(null=True)
    haulage_type = CharField(index=True, null=True, default='merchant')
    generalized_data = BinaryJSONField(null=True)
    container_size = CharField(index=True, null=True)
    created_at = DateTimeField(default=datetime.datetime.now, index=True)
    updated_at = DateTimeField(default=datetime.datetime.now, index=True)

    class Meta:
        table_name = 'haulage_freight_rate_rule_sets'

    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(HaulageFreightRateRuleSet, self).save(*args, **kwargs)
