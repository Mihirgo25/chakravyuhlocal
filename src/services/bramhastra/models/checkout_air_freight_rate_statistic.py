from peewee import Model, BigAutoField, UUIDField, CharField, IntegerField
from datetime import datetime
from database.db_session import db
from playhouse.postgres_ext import DateTimeTZField


class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class CheckoutAirFreightRateStatistic(BaseModel):
    id = BigAutoField()
    spot_search_id = UUIDField()
    checkout_id = UUIDField()
    checkout_air_freight_rate_services_id = UUIDField(null=True)
    validity_id = UUIDField()
    rate_id = UUIDField()
    sell_quotation_id = UUIDField(null=True)
    buy_quotation_id = UUIDField(null=True)
    shipment_id = UUIDField(null=True)
    created_at = DateTimeTZField(default = datetime.utcnow())
    updated_at = DateTimeTZField(default = datetime.utcnow())
    status = CharField(default = 'active')
    sign = IntegerField(default=1)
    version = IntegerField(default=1)

    class Meta:
        table_name = "checkout_air_freight_rate_statistics"
