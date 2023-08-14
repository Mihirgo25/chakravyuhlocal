from peewee import *
from database.db_session import db
import datetime
from playhouse.postgres_ext import *
from configs.fcl_freight_rate_constants import VALUE_PROPOSITIONS
from fastapi import HTTPException

class BaseModel(Model):
    class Meta:
        database = db

class FclFreightRateProperties(BaseModel):
    id = BigAutoField(index=True,primary_key=True)
    rate_id = UUIDField(index=True,unique=True)
    created_at = DateTimeField(default=datetime.datetime.now())
    updated_at = DateTimeField(default=datetime.datetime.now())
    value_props = BinaryJSONField(default=[{"name": "confirmed_space_and_inventory", "free_limit": None}])
    t_n_c = ArrayField(constraints=[SQL("DEFAULT '{}'::character varying[]")], field_class=TextField, null=True)
    available_inventory = IntegerField(default=100)
    used_inventory = IntegerField(default=0)
    shipment_count = IntegerField(default=0)
    volume_count = IntegerField(default=0)
    
    def save(self, *args, **kwargs):      
        self.updated_at = datetime.datetime.now()
        return super(FclFreightRateProperties, self).save(*args, **kwargs)

    class Meta:
        db_table = "fcl_freight_rate_properties"

    def validate_value_properties(self):
      value_props = self.value_props
      for prop in value_props:
        name = prop.get('name')
        if name not in VALUE_PROPOSITIONS:
            raise HTTPException(status_code=400, detail='Invalid rate_type parameter')
        
      return True


