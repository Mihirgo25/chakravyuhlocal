from peewee import (
    Model,
    BigAutoField,
    UUIDField,
    CharField,
    IntegerField,
    BigIntegerField,
)
from datetime import datetime
from database.db_session import db
from playhouse.postgres_ext import DateTimeTZField, FloatField


class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True


class CheckoutFclFreightRateStatistic(BaseModel):
    id = BigAutoField()
    fcl_freight_rate_statistic_id = BigIntegerField(index = True)
    source = CharField(index = True)
    source_id = UUIDField(index = True)
    checkout_id = UUIDField(index = True)
    checkout_fcl_freight_service_id = UUIDField(null=True)
    validity_id = UUIDField(index = True)
    rate_id = UUIDField(index = True)
    sell_quotation_id = UUIDField(null=True)
    buy_quotation_id = UUIDField(null=True)
    shipment_id = UUIDField(null=True, index = True)
    created_at = DateTimeTZField(default=datetime.utcnow())
    updated_at = DateTimeTZField(default=datetime.utcnow(), index = True)
    total_buy_price = FloatField(null=True)
    currency = CharField(null=True)
    importer_exporter_id = UUIDField(null=True, index = True)
    status = CharField(default="active")
    sign = IntegerField(default=1)
    version = IntegerField(default=1)
    operation_created_at = DateTimeTZField(default=datetime.utcnow())
    operation_updated_at = DateTimeTZField(default=datetime.utcnow(), index=True)

    def save(self, *args, **kwargs):
        self.operation_updated_at = datetime.utcnow()
        return super(CheckoutFclFreightRateStatistic, self).save(*args, **kwargs)

    class Meta:
        table_name = "checkout_fcl_freight_rate_statistics"
