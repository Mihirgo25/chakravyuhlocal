from peewee import Model, BigAutoField, UUIDField, CharField, IntegerField, BigIntegerField, FloatField, TextField
from datetime import datetime
from database.db_session import db
from playhouse.postgres_ext import DateTimeTZField


class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True


class ShipmentAirFreightRateStatistic(BaseModel):
    id = BigAutoField()
    air_freight_rate_statistic_id =  BigIntegerField()
    validity_id = UUIDField()
    rate_id =  UUIDField()
    shipment_id = UUIDField()
    shipment_serial_id = BigIntegerField()
    shipment_source = CharField()
    containers_count = IntegerField()
    cargo_weight_per_container = FloatField()
    buy_quotation_id = UUIDField()
    sell_quotation_id = UUIDField()
    shipment_state = CharField()
    shipment_cancelled = IntegerField()
    shipment_cancellation_reason = TextField()
    shipment_completed = IntegerField()
    shipment_aborted = IntegerField()
    shipment_in_progress = IntegerField()
    shipment_confirmed_by_importer_exporter = IntegerField()
    shipment_recieved = IntegerField()
    shipment_source_id = UUIDField()
    shipment_created_at = DateTimeTZField(default=datetime.utcnow())
    shipment_updated_at = DateTimeTZField(default=datetime.utcnow())
    shipment_service_id = UUIDField()
    shipment_service_state = TextField()
    shipment_service_is_active = TextField()
    shipment_service_created_at = DateTimeTZField(default=datetime.utcnow())
    shipment_service_updated_at = DateTimeTZField(default=datetime.utcnow())
    shipment_service_cancellation_reason  = TextField()
    sign = IntegerField(default= 1)
    version = IntegerField(default=1)
    operation_created_at = DateTimeTZField(default=datetime.utcnow())
    operation_updated_at = DateTimeTZField(default=datetime.utcnow())

    class Meta:
        table_name = "shipment_air_freight_rate_statistics"
