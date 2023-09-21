from peewee import (
    Model,
    BigIntegerField,
    UUIDField,
    IntegerField,
    FloatField,
    DateField,
)
from database.db_session import db
from playhouse.postgres_ext import (
    DateTimeTZField,
    BigAutoField,
    TextField,
    CharField,
    ForeignKeyField,
)
from datetime import datetime
from services.bramhastra.enums import ImportTypes
from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)
import sys


class BaseModel(Model):
    class Meta:
        database = db


class FclFreightAction(BaseModel):
    id = BigAutoField()
    fcl_freight_rate_statistic_id = ForeignKeyField(FclFreightRateStatistic)
    origin_port_id = UUIDField(index=True)
    destination_port_id = UUIDField(index=True)
    origin_main_port_id = UUIDField(null=True, index=True)
    destination_main_port_id = UUIDField(null=True, index=True)
    origin_region_id = UUIDField(null=True, index=True)
    destination_region_id = UUIDField(null=True, index=True)
    origin_country_id = UUIDField(index=True)
    destination_country_id = UUIDField(index=True)
    origin_continent_id = UUIDField(null=True, index=True)
    destination_continent_id = UUIDField(null=True, index=True)
    origin_trade_id = UUIDField(null=True, index=True)
    destination_trade_id = UUIDField(null=True, index=True)
    commodity = TextField(null=True, index=True)
    container_size = TextField(null=True, index=True)
    container_type = TextField(null=True, index=True)
    service_provider_id = UUIDField(null=True, index=True)
    containers_count = IntegerField(default=0)
    rate_id = UUIDField(index=True)
    validity_id = UUIDField(index=True)
    bas_price = FloatField(default=0, null=True)
    bas_standard_price = FloatField(default=0, null=True)
    standard_price = FloatField(default=0, null=True)
    price = FloatField(default=0, null=True)
    currency = CharField(max_length=3)
    market_price = FloatField(default=0, null=True)
    bas_currency = CharField(max_length=3, null=True)
    mode = CharField(index=True)
    parent_mode = CharField(index=True)
    source = CharField(index=True)
    source_id = UUIDField(index=True)
    sourced_by_id = UUIDField(index=True, default="None")
    procured_by_id = UUIDField(index=True, default="None")
    performed_by_id = UUIDField(index=True, default="None")
    rate_type = CharField(default="None")
    validity_start = DateField()
    validity_end = DateField()
    shipping_line_id = UUIDField(null=True, index=True)
    importer_exporter_id = UUIDField(null=True, index=True)
    spot_search_id = UUIDField(index=True)
    spot_search_fcl_freight_service_id = UUIDField(null=True)
    spot_search = IntegerField(default=0)
    checkout_source = CharField()
    checkout_id = UUIDField(null=True, index=True)
    checkout_fcl_freight_service_id = UUIDField(null=True)
    checkout = IntegerField(default=0)
    shipment = IntegerField(default=0)
    shipment_id = UUIDField(null=True, index=True)
    shipment_serial_id = BigIntegerField()
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
    shipment_state = TextField(null=True)
    shipment_created_at = DateTimeTZField(null=True)
    shipment_updated_at = DateTimeTZField(null=True)
    shipment_cancellation_reason = TextField(null=True)
    shipment_service_state = CharField(null=True)
    shipment_service_is_active = CharField(null=True)
    shipment_service_created_at = DateTimeTZField(null=True)
    shipment_service_updated_at = DateTimeTZField(null=True)
    shipment_service_cancellation_reason = TextField(null=True)
    disliked = IntegerField(default=0)
    liked = IntegerField(default=0)
    feedback_id = UUIDField(index=True, null=True)
    so1_select = IntegerField(default=0)
    selected_bas_standard_price = FloatField(default=0)
    bas_standard_price_accuracy = FloatField(default=-sys.float_info.max)
    bas_standard_price_diff_from_selected_rate = FloatField(default=0)
    selected_fcl_freight_rate_statistic_id = BigIntegerField(default=0)
    selected_rate_id = UUIDField(index=True, null=True)
    selected_validity_id = UUIDField(index=True, null=True)
    revenue_desk_visit = IntegerField(default=0)
    revenue_desk_select = IntegerField(default=0)
    given_priority = IntegerField(default=0)
    rate_created_at = DateTimeTZField(index=True)
    rate_updated_at = DateTimeTZField(index=True)
    validity_updated_at = DateTimeTZField(index=True)
    validity_created_at = DateTimeTZField(index=True)
    created_at = DateTimeTZField(index=True)
    updated_at = DateTimeTZField(index=True)
    operation_created_at = DateTimeTZField(default=datetime.utcnow())
    operation_updated_at = DateTimeTZField(default=datetime.utcnow(), index=True)
    sign = IntegerField(default=1)
    version = IntegerField(default=1)

    def save(self, *args, **kwargs):
        self.operation_updated_at = datetime.utcnow()
        self.created_at = self.updated_at
        return super(FclFreightAction, self).save(*args, **kwargs)

    def refresh(self):
        return type(self).get(self._pk_expr())

    class Meta:
        table_name = "fcl_freight_actions"

        CLICK_KEYS = [
            "origin_continent_id",
            "parent_mode",
            "origin_country_id",
            "container_size",
            "rate_id",
            "id",
        ]

    IMPORT_TYPE = ImportTypes.csv.value
