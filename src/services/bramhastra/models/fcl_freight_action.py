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
    ArrayField,
)
from datetime import datetime
from services.bramhastra.constants import DEFAULT_UUID, DEFAULT_ENUM
from services.bramhastra.enums import FclModes, ImportTypes


class BaseModel(Model):
    class Meta:
        database = db


class FclFreightAction(BaseModel):
    id = BigAutoField()
    fcl_freight_rate_statistic_id = BigIntegerField(index=True, null=True)
    origin_port_id = UUIDField(index=True, default=DEFAULT_UUID)
    destination_port_id = UUIDField(index=True, default=DEFAULT_UUID)
    origin_main_port_id = UUIDField(null=True, index=True, default=DEFAULT_UUID)
    destination_main_port_id = UUIDField(null=True, index=True, default=DEFAULT_UUID)
    origin_region_id = UUIDField(null=True, index=True, default=DEFAULT_UUID)
    destination_region_id = UUIDField(null=True, index=True, default=DEFAULT_UUID)
    origin_country_id = UUIDField(index=True, default=DEFAULT_UUID)
    destination_country_id = UUIDField(index=True, default=DEFAULT_UUID)
    origin_continent_id = UUIDField(null=True, index=True, default=DEFAULT_UUID)
    destination_continent_id = UUIDField(null=True, index=True, default=DEFAULT_UUID)
    origin_trade_id = UUIDField(null=True, index=True, default=DEFAULT_UUID)
    destination_trade_id = UUIDField(null=True, index=True, default=DEFAULT_UUID)
    commodity = TextField(null=True, index=True)
    container_size = TextField(null=True, index=True)
    container_type = TextField(null=True, index=True)
    service_provider_id = UUIDField(null=True, index=True, default=DEFAULT_UUID)
    rate_id = UUIDField(index=True, default=DEFAULT_UUID)
    validity_id = UUIDField(index=True, default=DEFAULT_UUID)
    bas_price = FloatField(default=0, null=True)
    bas_standard_price = FloatField(default=0, null=True)
    standard_price = FloatField(default=0, null=True)
    price = FloatField(default=0, null=True)
    currency = CharField(max_length=3, null=True)
    market_price = FloatField(default=0, null=True)
    bas_currency = CharField(max_length=3, null=True)
    mode = CharField(index=True, null=True)
    parent_mode = CharField(index=True, null=True)
    parent_rate_mode = CharField(index=True, null=True)
    source = CharField(index=True, default=FclModes.manual.value, null=True)
    source_id = UUIDField(index=True, default=DEFAULT_UUID, null=True)
    sourced_by_id = UUIDField(index=True, default=DEFAULT_UUID, null=True)
    procured_by_id = UUIDField(index=True, default=DEFAULT_UUID, null=True)
    performed_by_id = UUIDField(index=True, default=DEFAULT_UUID, null=True)
    rate_type = CharField(null=True)
    validity_start = DateField(null=True)
    validity_end = DateField(null=True)
    shipping_line_id = UUIDField(null=True, index=True, default=DEFAULT_UUID)
    importer_exporter_id = UUIDField(null=True, index=True, default=DEFAULT_UUID)
    spot_search_id = UUIDField(index=True, default=DEFAULT_UUID)
    spot_search_fcl_freight_service_id = UUIDField(null=True, default=DEFAULT_UUID)
    spot_search = IntegerField(default=0, null=True)
    checkout_source = CharField(null=True)
    checkout_id = UUIDField(null=True, index=True, default=DEFAULT_UUID)
    checkout_fcl_freight_service_id = UUIDField(null=True, default=DEFAULT_UUID)
    checkout = IntegerField(default=0, null=True)
    checkout_created_at = DateTimeTZField(null=True)
    shipment = IntegerField(default=0, null=True)
    shipment_id = UUIDField(null=True, index=True, default=DEFAULT_UUID)
    shipment_source = CharField(null=True)
    containers_count = IntegerField(null=True, default=0)
    cargo_weight_per_container = FloatField(null=True, default=0)
    shipment_state = CharField(null=True, default=DEFAULT_ENUM)
    shipment_service_id = UUIDField(null=True, default=DEFAULT_UUID)
    shipment_cancellation_reason = TextField(null=True, index=True)
    shipment_source_id = UUIDField(null=True, default=DEFAULT_UUID)
    shipment_created_at = DateTimeTZField(null=True)
    shipment_updated_at = DateTimeTZField(null=True)
    shipment_service_state = CharField(null=True, default=DEFAULT_ENUM)
    shipment_service_is_active = CharField(null=True)
    shipment_service_created_at = DateTimeTZField(null=True)
    shipment_service_updated_at = DateTimeTZField(null=True)
    shipment_service_cancellation_reason = TextField(null=True)
    feedback_type = CharField(null=True, default=DEFAULT_ENUM)
    feedback_state = CharField(null=True, default=DEFAULT_ENUM)
    feedback_ids = ArrayField(UUIDField, null=True)
    rate_request_state = CharField(null=True, default=DEFAULT_ENUM)
    rate_requested_ids = ArrayField(UUIDField, null=True)
    selected_bas_standard_price = FloatField(default=0, null=True)
    bas_standard_price_accuracy = FloatField(default=0, null=True) 
    bas_standard_price_diff_from_selected_rate = FloatField(default=0, null=True)
    selected_fcl_freight_rate_statistic_id = BigIntegerField(default=0, null=True)
    selected_rate_id = UUIDField(index=True, null=True, default=DEFAULT_UUID)
    selected_validity_id = UUIDField(index=True, null=True, default=DEFAULT_UUID)
    selected_type = CharField(index=True, null=True)
    revenue_desk_state = CharField(null=True, default=DEFAULT_ENUM)
    given_priority = IntegerField(default=0, null=True)
    rate_created_at = DateTimeTZField(index=True, null=True)
    rate_updated_at = DateTimeTZField(index=True, null=True)
    validity_created_at = DateTimeTZField(index=True, null=True)
    validity_updated_at = DateTimeTZField(index=True, null=True)
    created_at = DateTimeTZField(index=True, default=datetime.utcnow())
    updated_at = DateTimeTZField(index=True, default=datetime.utcnow())
    operation_created_at = DateTimeTZField(default=datetime.utcnow())
    operation_updated_at = DateTimeTZField(default=datetime.utcnow(), index=True)

    def save(self, *args, **kwargs):
        self.operation_updated_at = datetime.utcnow()
        return super(FclFreightAction, self).save(*args, **kwargs)
    
    @classmethod
    def update(cls, *args, **kwargs):
        kwargs['updated_at'] = datetime.now()
        return super().update(*args, **kwargs)

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
