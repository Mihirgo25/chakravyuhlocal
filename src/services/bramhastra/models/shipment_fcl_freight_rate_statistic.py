from peewee import Model, BigAutoField, UUIDField, CharField, IntegerField
import datetime
from database.db_session import db
from playhouse.postgres_ext import DateTimeTZField, BinaryJSONField


class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True


class ShipmentFclFreightRateStatistic(BaseModel):
    id = BigAutoField()
    spot_search_id = UUIDField()
    spot_search_fcl_customs_services_id = UUIDField()
    checkout_id = UUIDField()
    checkout_fcl_freight_rate_services_id = UUIDField(null=True)
    sell_quotation_id = UUIDField()
    buy_quotation_id = UUIDField()
    validity_id = UUIDField()
    rate_id = UUIDField()
    shipment_id = UUIDField(null=True)
    shipment_fcl_freight_rate_services_id = UUIDField(null=True)
    cancellation_reason = CharField(default = '')
    state = CharField()
    is_active = CharField()
    created_at = DateTimeTZField()
    updated_at = DateTimeTZField()
    status = CharField()
    state = IntegerField(default=1)
    version = IntegerField()

    class Meta:
        table_name = "shipment_fcl_freight_rate_services_statistics"
