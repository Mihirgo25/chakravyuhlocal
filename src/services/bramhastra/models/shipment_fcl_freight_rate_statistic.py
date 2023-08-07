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
    shipment_id = UUIDField()
    shipment_fcl_freight_service_id = UUIDField()
    service_state = TextField()
    service_is_active = BooleanField()
    service_cancellation_reason = CharField()
    service_created_at = DateTimeTZField()
    service_updated_at = DateTimeTZField()
    shipping_line_id = UUIDField()
    service_provider_id = UUIDField()
    serial_id = BigIntegerField()
    importer_exporter_id = UUIDField()
    shipment_type = CharField()
    services = ArrayField(CharField)
    source = CharField()
    source_id = UUIDField()
    state = TextField()
    cancellation_reason = TextField()
    sell_quotation_id = UUIDField()
    total_price = FloatField(default=0)
    total_price_discounted = FloatField(default=0)
    tax_price = FloatField(default=0)
    tax_price_discounted = FloatField(default=0)
    tax_total_price = FloatField(default=0)
    tax_total_price_discounted = FloatField(default=0)
    currency = CharField(max_length=3)
    standard_total_price = FloatField()
    created_at = DateTimeTZField(default=datetime.utcnow())
    updated_at = DateTimeTZField(default=datetime.utcnow())
    sign = IntegerField(default=1)
    version = IntegerField(default=1)

    class Meta:
        table_name = "shipment_fcl_freight_rate_services_statistics"
