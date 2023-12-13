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
    BooleanField
)
from datetime import datetime
from services.bramhastra.constants import DEFAULT_UUID, DEFAULT_ENUM
from configs.env import DEFAULT_USER_ID
from services.bramhastra.enums import ImportTypes


class BaseModel(Model):
    class Meta:
        database = db


class AirFreightAction(BaseModel):
    id = BigAutoField(primary_key = True)
    origin_airport_id = UUIDField(index=True, default=DEFAULT_UUID)
    destination_airport_id = UUIDField(index=True, default=DEFAULT_UUID)
    origin_region_id = UUIDField(index=True, default=DEFAULT_UUID)
    destination_region_id = UUIDField(index=True, default=DEFAULT_UUID)
    origin_country_id = UUIDField(index=True, default=DEFAULT_UUID)
    destination_country_id = UUIDField(index=True, default=DEFAULT_UUID)
    origin_continent_id = UUIDField(index=True, default=DEFAULT_UUID)
    destination_continent_id = UUIDField(index=True, default=DEFAULT_UUID)
    origin_trade_id = UUIDField(index=True, default=DEFAULT_UUID)
    destination_trade_id = UUIDField(index=True, default=DEFAULT_UUID)
    commodity = TextField(null=True, index=True)
    commodity_type = TextField(null=True, index=True)
    commodity_subtype = TextField(null=True, index=True)
    operation_type = TextField(null=True, index=True)
    stacking_type = TextField(null=True, index=True)
    shipment_type = TextField(null=True, index=True)
    service_provider_id = UUIDField(default=DEFAULT_UUID)
    rate_id = UUIDField(default=DEFAULT_UUID)
    validity_id = UUIDField(default=DEFAULT_UUID)
    standard_price = FloatField(default=0, null=True) 
    price = FloatField(default=0, null=True) 
    currency = TextField(null=True)
    market_price = FloatField(default=0, null=True) 
    mode = TextField(null=True)
    parent_mode = TextField(null=True)
    parent_rate_mode = TextField(null=True)
    source = TextField(null=True)
    source_id = UUIDField(default=DEFAULT_UUID)
    sourced_by_id = UUIDField(default=DEFAULT_UUID)
    procured_by_id = UUIDField(default=DEFAULT_UUID)
    performed_by_id = UUIDField(default=DEFAULT_UUID)
    rate_type = TextField(null=True)
    validity_start = DateTimeTZField(default=datetime.now)
    validity_end = DateTimeTZField(default=datetime.now)
    airline_id = UUIDField(default=DEFAULT_UUID)
    importer_exporter_id = UUIDField(default=DEFAULT_UUID)
    spot_search_id = UUIDField(default=DEFAULT_UUID)
    spot_search_air_freight_service_id = UUIDField(default=DEFAULT_UUID)
    spot_search = IntegerField(default=0, null=True)
    checkout_source = TextField(null=True)
    checkout_id = UUIDField(default=DEFAULT_UUID)
    checkout_fcl_freight_service_id = UUIDField(default=DEFAULT_UUID)
    checkout = IntegerField(default=0, null=True)
    checkout_created_at = DateTimeTZField(default=datetime.now)
    shipment = IntegerField(default=0, null=True)
    shipment_id = UUIDField(default=DEFAULT_UUID)
    shipment_source = TextField(null=True)
    shipment_state = TextField(null=True)
    shipment_service_id = UUIDField(default=DEFAULT_UUID)
    shipment_cancellation_reason = TextField(null=True)
    shipment_source_id = UUIDField(default=DEFAULT_UUID)
    shipment_created_at = DateTimeTZField(default=datetime.now)
    shipment_updated_at = DateTimeTZField(default=datetime.now)
    shipment_service_state = TextField(null=True)
    shipment_service_is_active = TextField(null=True)
    shipment_service_created_at = DateTimeTZField(default=datetime.now)
    shipment_service_updated_at = DateTimeTZField(default=datetime.now)
    shipment_cancellation_reason = TextField(null=True)
    feedback_type = TextField(null=True)
    feedback_state = TextField(null=True)
    feedback_ids = ArrayField(UUIDField, null=True)
    rate_request_state = TextField(null=True)
    rate_requested_ids = ArrayField(UUIDField, null=True)
    selected_standard_price = FloatField(default=0, null=True)
    standard_price_accuracy = FloatField(default=0, null=True)
    standard_price_diff_from_selected_rate = FloatField(default=0, null=True)
    selected_air_freight_rate_statistic_id = BigIntegerField(index=True, null=True)
    selected_rate_id = UUIDField(default=DEFAULT_UUID)
    selected_validity_id = UUIDField(default=DEFAULT_UUID)
    selected_type = TextField(null=True)
    revenue_desk_state = TextField(null=True)
    given_priority = IntegerField(default=0, null=True)
    rate_created_at = DateTimeTZField(default=datetime.now)
    rate_updated_at = DateTimeTZField(default=datetime.now)
    validity_created_at = DateTimeTZField(default=datetime.now)
    validity_updated_at = DateTimeTZField(default=datetime.now)
    created_at = DateTimeTZField(default=datetime.now)
    updated_at = DateTimeTZField(default=datetime.now)
    operation_created_at = DateTimeTZField(default=datetime.now)
    operation_updated_at = DateTimeTZField(default=datetime.now)

    def save(self, *args, **kwargs):
        self.operation_updated_at = datetime.now()
        return super(AirFreightAction, self).save(*args, **kwargs)
    
    @classmethod
    def update(cls, *args, **kwargs):
        kwargs['operation_updated_at'] = datetime.now()
        return super().update(*args, **kwargs)

    def refresh(self):
        return type(self).get(self._pk_expr())

    class Meta:
        table_name = "air_freight_actions"

        CLICK_KEYS = [
            "origin_continent_id",
            "parent_mode",
            "origin_country_id",
            "container_size",
            "rate_id",
            "id",
        ]

    IMPORT_TYPE = ImportTypes.csv.value