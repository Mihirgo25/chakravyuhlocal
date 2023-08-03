from peewee import Model, BigAutoField, UUIDField, CharField, IntegerField, FloatField
from datetime import datetime
from database.db_session import db
from playhouse.postgres_ext import DateTimeTZField, BinaryJSONField


class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True


class ShipmentFclFreightRateStatistic(BaseModel):
    id = BigAutoField()
    spot_search_id = UUIDField()
    checkout_id = UUIDField()
    shipping_line_id = UUIDField()
    service_provider_id = UUIDField()
    shipment_state = CharField()
    shipment_service_state  = CharField()
    shipment_service_is_active = CharField()
    shipment_service_cancellation_reason = CharField()
    shipment_cancellation_reason = CharField()
    checkout_fcl_freight_services_id = UUIDField()
    sell_quotation_id = UUIDField(null = True)
    buy_quotation_id = UUIDField()
    total_buy_price = FloatField()
    total_buy_tax_price = FloatField()
    currency = CharField()
    global_total_buy_price = FloatField()
    global_total_buy_tax_price = FloatField()
    validity_id = UUIDField()
    rate_id = UUIDField()
    shipment_id = UUIDField(null=True)
    cancellation_reason = CharField(default = '')
    created_at = DateTimeTZField(default = datetime.utcnow())
    updated_at = DateTimeTZField(default = datetime.utcnow())
    status = CharField(default = 'active')
    sign = IntegerField(default=1)
    version = IntegerField(default=1)

    class Meta:
        table_name = "shipment_fcl_freight_rate_services_statistics"
