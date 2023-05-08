from peewee import *
from database.db_session import db
import uuid
import datetime
from services.rail_rate.models.rail_rates_india import RailRatesIndia

class BaseModel(Model):
    class Meta:
        database = db
class CommodityMapping(BaseModel):
    id = UUIDField(
        primary_key=True,
        constraints=[SQL("DEFAULT uuid_generate_v4()")],
        default=uuid.uuid4,
    )
    commodity_name = CharField(index=True)
    base_class = CharField(index=True)
    commodity_type = CharField(index=True)
    # packing_condition = CharField(index=True)
    # risk_rate = CharField(index=True)
    created_at = DateTimeField(default=datetime.datetime.now, index=True)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = 'commodity_mapping1'

    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(CommodityMapping, self).save(*args, **kwargs)
