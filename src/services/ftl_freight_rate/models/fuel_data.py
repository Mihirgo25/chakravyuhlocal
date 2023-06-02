from peewee import *
from database.db_session import db
import datetime
import uuid

class BaseModel(Model):
    class Meta:
        database = db
class FuelData(BaseModel):
    id = BigAutoField(primary_key=True)
    location_id = UUIDField(null=True, index=True)
    location_type = CharField(null=False, index=True)
    currency = CharField(null=False)
    fuel_unit = CharField(null=False)
    fuel_type = CharField(null=False, index=True)
    fuel_price = DecimalField(null=False,max_digits = 10, decimal_places= 6)
    created_at = DateTimeField(null=False, default=datetime.datetime.now())
    updated_at = DateTimeField(null=False, default=datetime.datetime.now())

    class Meta:
        table_name = "fuel_data"

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(FuelData, self).save(*args, **kwargs)
