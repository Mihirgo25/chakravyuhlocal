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
from playhouse.postgres_ext import DateTimeTZField


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
    shipment_id = UUIDField(null=True, index=True)
    shipment_serial_id = BigIntegerField(null = True)
    shipment_source = CharField()
    containers_count = IntegerField()
    cargo_weight_per_container = FloatField()
    shipment_state = TextField(null=True)
    shipment_service_id = UUIDField(null=True)
    shipment_cancelled = IntegerField(default=0)
    shipment_cancellation_reason = TextField(default="None", index=True)
    shipment_completed = IntegerField(default=0)
    shipment_aborted = IntegerField(default=0)
    shipment_in_progress = IntegerField(default=0)
    shipment_confirmed_by_importer_exporter = IntegerField(default=0)
    shipment_recieved = IntegerField(default=0)
    shipment_source_id = UUIDField(null=True)
    shipment_created_at = DateTimeTZField(null=True)
    shipment_updated_at = DateTimeTZField(null=True)
    shipment_service_state = CharField(null=True)
    shipment_service_is_active = CharField(null=True)
    shipment_service_created_at = DateTimeTZField(null=True)
    shipment_service_updated_at = DateTimeTZField(null=True)
    shipment_service_cancellation_reason = TextField(null=True)
    sign = IntegerField(default=1)
    version = IntegerField(default=1)
    operation_created_at = DateTimeTZField(default=datetime.utcnow())
    operation_updated_at = DateTimeTZField(default=datetime.utcnow(), index=True)

    def save(self, *args, **kwargs):
        self.operation_updated_at = datetime.utcnow()
        return super(ShipmentFclFreightRateStatistic, self).save(*args, **kwargs)

    class Meta:
        table_name = "shipment_fcl_freight_rate_statistics"
