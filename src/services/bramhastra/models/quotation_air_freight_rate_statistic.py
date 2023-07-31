from peewee import Model, BigAutoField, UUIDField, CharField, IntegerField
from datetime import datetime
from database.db_session import db
from playhouse.postgres_ext import DateTimeTZField


class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True


class QuotationAirFreightRateStatistic(BaseModel):
    id = BigAutoField()
    validity_id = UUIDField()
    rate_id = UUIDField()
    spot_search_id = UUIDField()
    spot_search_air_customs_services_id = UUIDField()
    checkout_id = UUIDField()
    checkout_air_freight_rate_services_id = UUIDField(null=True)
    sell_quotation_id = UUIDField()
    buy_quotation_id = UUIDField()
    shipment_id = UUIDField(null=True)
    shipment_air_freight_rate_services_id = UUIDField(null=True)
    cancellation_reason = CharField(default = '')
    is_active = CharField()
    created_at = DateTimeTZField(default = datetime.utcnow())
    updated_at = DateTimeTZField(default = datetime.utcnow())
    status = CharField(default = 'active')
    sign = IntegerField(default=1)
    version = IntegerField(default=1)

    class Meta:
        table_name = "quotation_air_freight_rate_statistics"
