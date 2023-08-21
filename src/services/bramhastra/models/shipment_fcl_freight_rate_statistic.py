from peewee import (
    Model,
    UUIDField,
    CharField,
    IntegerField,
    FloatField,
    BigIntegerField,
    TextField,
)
from datetime import datetime
from database.db_session import db
from playhouse.postgres_ext import DateTimeTZField, ArrayField, BooleanField


class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True


class ShipmentFclFreightRateStatistic(BaseModel):
    id = BigIntegerField(sequence="shipment_fcl_freight_rate_services_statistics_seq")
    fcl_freight_rate_statistic_id = BigIntegerField()
    rate_id = UUIDField(null=True)
    validity_id = UUIDField(
        null=True
    )  # this rate and validity id is different from what fcl_freight_rate_statistic table implies
    shipment_id = UUIDField(null=True)
    shipment_fcl_freight_service_id = UUIDField(null=True)
    service_state = TextField(null=True)
    service_is_active = BooleanField(null=True)
    service_cancellation_reason = CharField(null=True)
    service_created_at = DateTimeTZField(default=datetime.utcnow())
    service_updated_at = DateTimeTZField(default=datetime.utcnow())
    shipping_line_id = UUIDField(null=True)
    service_provider_id = UUIDField(null=True)
    serial_id = BigIntegerField(null=True)
    importer_exporter_id = UUIDField(null=True)
    shipment_type = CharField(null=True)
    services = ArrayField(CharField)
    source = CharField(null=True)
    source_id = UUIDField(null=True)
    state = TextField(null=True)
    cancellation_reason = TextField(null=True)
    buy_quotation_id = UUIDField(null=True)
    buy_quotation_created_at = DateTimeTZField(default=datetime.utcnow())
    buy_quotation_updated_at = DateTimeTZField(default=datetime.utcnow())
    is_deleted = BooleanField(null=True)
    total_price = FloatField(default=0,null=True)
    total_price_discounted = FloatField(default=0,null=True)
    tax_price = FloatField(default=0,null=True)
    tax_price_discounted = FloatField(default=0,null=True)
    tax_total_price = FloatField(default=0,null=True)
    tax_total_price_discounted = FloatField(default=0,null=True)
    currency = CharField(max_length=3)
    standard_total_price = FloatField(null=True)
    created_at = DateTimeTZField(default=datetime.utcnow())
    updated_at = DateTimeTZField(default=datetime.utcnow())
    sign = IntegerField(default=1)
    version = IntegerField(default=1)

    class Meta:
        table_name = "shipment_fcl_freight_rate_statistics"
