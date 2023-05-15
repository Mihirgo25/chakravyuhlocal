from peewee import *
from database.db_session import db
import uuid
import datetime
from playhouse.postgres_ext import *



class BaseModel(Model):
    class Meta:
        database = db
class HaulageFreightRateRuleSet(BaseModel):
    id = UUIDField(
        primary_key=True,
        constraints=[SQL("DEFAULT uuid_generate_v4()")],
        default=uuid.uuid4,
    )
    distance = FloatField(index=True)
    wagon_count = IntegerField(index=True, null=True)
    status = CharField(index=True, default='active')
    train_load_type = CharField(index=True)
    commodity_class_type = CharField(index=True)
    commodity_type = CharField(index=True, null=True)
    wagon_type = CharField(index=True, null=True)
    base_rate = IntegerField()
    base_rate_unit = CharField(index=True, null=True)
    country_code = CharField(index=True)
    currency = CharField(index=True)
    transit_time = IntegerField(null=True)
    pollution_fee = FloatField(null=True)
    climate_change_fee = FloatField(null=True)
    noise_pollution_fee = FloatField(null=True)
    indirect_pollution_fee = FloatField(null=True)
    railway_electrification_surcharge = FloatField(null=True)
    railway_loading_surcharge = FloatField(null=True)
    container_usage_surcharge = FloatField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now, index=True)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = 'haulage_freight_rate_rule_sets'

    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(HaulageFreightRateRuleSet, self).save(*args, **kwargs)
