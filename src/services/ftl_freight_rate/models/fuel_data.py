from peewee import *
from database.db_session import db
import datetime


class BaseModel(Model):
    class Meta:
        database = db
class FuelData(BaseModel):
    id = UUIDField(
        primary_key=True,
        constraints=[SQL("DEFAULT uuid_generate_v4()")],
        default=uuid.uuid4,
    )
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
