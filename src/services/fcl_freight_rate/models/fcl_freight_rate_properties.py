from peewee import *
from database.db_session import db
import datetime
from playhouse.postgres_ext import *
from configs.fcl_freight_rate_constants import VALUE_PROPOSITIONS

class BaseModel(Model):
    class Meta:
        database = db

class RateProperties(BaseModel):
    id = BigAutoField(index=True,primary_key=True)
    rate_id = UUIDField(index=True)
    created_at = DateTimeField(null=True)
    updated_at = DateTimeField(null=True)
    value_props = BinaryJSONField(null=True)
    t_n_c = ArrayField(null=True)
    available_inventory = IntegerField(default=100)
    used_inventory = IntegerField(default=0)
    shipment_count = IntegerField(default=0)
    volume_count = IntegerField(default=0)

    class Meta:
        db_table = "rate_properties"

    # def validate_rate_id(self):
    #     if self.rate_id and self.rate_id in :
    #         return True
    #   return False

    def validate_value_props(self):
      if self.value_props and self.value_props in VALUE_PROPOSITIONS:
        return True
      return False

