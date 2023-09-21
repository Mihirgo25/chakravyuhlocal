from peewee import (
    Model,
    BigIntegerField,
    UUIDField,
    IntegerField,
    FloatField,
    DateField
)
from database.db_session import db
from playhouse.postgres_ext import (
    DateTimeTZField,
    BigAutoField,
    TextField,
    CharField,
    ForeignKeyField,
    ArrayField
)
from datetime import datetime
from services.bramhastra.enums import ImportTypes
from services.bramhastra.models.fcl_freight_rate_statistic import FclFreightRateStatistic
from services.bramhastra.constants import DEFAULT_UUID
import sys


class BaseModel(Model):
    class Meta:
        database = db


class FclFreightAction(BaseModel):
    id = BigAutoField()
    fcl_freight_rate_statistic_id = BigIntegerField(null=True)
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
    containers_count = IntegerField(default=0)
    rate_id = UUIDField(index=True, default=DEFAULT_UUID)
    validity_id = UUIDField(index=True, default=DEFAULT_UUID)
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
    source_id = UUIDField(index=True, default=DEFAULT_UUID)
    sourced_by_id = UUIDField(index=True, default=DEFAULT_UUID)
    procured_by_id = UUIDField(index=True, default=DEFAULT_UUID)
    performed_by_id = UUIDField(index=True, default=DEFAULT_UUID)
    rate_type = CharField(default="None")
    validity_start = DateField()
    validity_end = DateField()
    shipping_line_id = UUIDField(null=True, index=True, default=DEFAULT_UUID)
    spot_search_id = UUIDField(index=True, default=DEFAULT_UUID)
    spot_search_fcl_freight_service_id = UUIDField(null=True, default=DEFAULT_UUID)
    spot_search = IntegerField(default=0)
    checkout_id = UUIDField(null=True, index=True, default=DEFAULT_UUID)
    checkout_fcl_freight_service_id = UUIDField(null=True, default=DEFAULT_UUID)
    checkout = IntegerField(default=0)
    shipment_id = UUIDField(null=True, index=True, default=DEFAULT_UUID)
    shipment_fcl_freight_service_id = UUIDField(null=True, default=DEFAULT_UUID)
    service_state = TextField(default="None", index=True)
    service_cancellation_reason = TextField(default="None", index=True)
    shipment = IntegerField(default=0)
    disliked = IntegerField(default=0)
    liked = IntegerField(default=0)
    rate_request_ids = ArrayField(UUIDField, null=True)
    feedback_ids = ArrayField(UUIDField, null=True)
    so1_select = IntegerField()
    selected_bas_standard_price = FloatField(default=0)
    bas_standard_price_accuracy = FloatField(default=-sys.float_info.max)
    bas_standard_price_diff_from_selected_rate = FloatField(default=0)
    selected_fcl_freight_rate_statistic_id = BigIntegerField(default=0)
    selected_rate_id = UUIDField(index=True, null=True, default=DEFAULT_UUID)
    selected_validity_id = UUIDField(index=True, null=True, default=DEFAULT_UUID)
    revenue_desk_visit = IntegerField(default=0)
    revenue_desk_select = IntegerField(default=0)
    given_priority = IntegerField(default=0)
    shipment_state = TextField(null=True)
    cancelled = IntegerField(default=0)
    cancellation_reason = TextField(default="None", index=True)
    completed = IntegerField(default=0)
    aborted = IntegerField(default=0)
    in_progress = IntegerField(default=0)
    confirmed_by_importer_exporter = IntegerField(default=0)
    recieved = IntegerField(default=0)
    rate_created_at = DateTimeTZField()
    rate_updated_at = DateTimeTZField(index=True)
    validity_updated_at = DateTimeTZField(index=True)
    validity_created_at = DateTimeTZField(index=True)
    created_at = DateTimeTZField()
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
