from peewee import Model, BigAutoField, UUIDField, CharField, IntegerField
import datetime
from database.db_session import db
from playhouse.postgres_ext import DateTimeTZField


class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class CheckoutFclFreightRateStatistic(BaseModel):
    id = BigAutoField()
    spot_search_id = UUIDField()
    spot_search_fcl_customs_services_id = UUIDField()
    checkout_id = UUIDField()
    checkout_fcl_freight_rate_services_id = UUIDField(null=True)
    validity_id = UUIDField()
    rate_id = UUIDField()
    sell_quotation_id = UUIDField()
    buy_quotation_id = UUIDField()
    shipment_id = UUIDField(null=True)
    created_at = DateTimeTZField(default = datetime.utcnow())
    updated_at = DateTimeTZField(default = datetime.utcnow())
    status = CharField(default = 'active')
    sign = IntegerField(default=1)
    version = IntegerField(default=1)

    class Meta:
        table_name = "checkout_fcl_freight_rate_statistics"
