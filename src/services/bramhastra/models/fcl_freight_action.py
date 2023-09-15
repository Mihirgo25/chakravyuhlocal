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
)
from datetime import datetime
from services.bramhastra.enums import ImportTypes
import sys


class BaseModel(Model):
    class Meta:
        database = db


class FclFreightAction(BaseModel):
    id = BigAutoField()
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
    shipping_line_id = UUIDField(null=True, index=True)
    service_provider_id = UUIDField(null=True, index=True)
    containers_count = IntegerField(default=0)
    rate_id = UUIDField(index=True)
    validity_id = UUIDField(index=True)
    bas_price = FloatField(default=0, null=True)
    bas_standard_price = FloatField(default=0, null=True)
    bas_currency = CharField(max_length=3, null=True)
    mode = CharField(index=True)
    parent_mode = CharField(index=True)
    source = CharField(index=True)
    source_id = UUIDField(index=True)
    standard_price = FloatField()
    market_price = FloatField()
    rate_type = CharField()
    validity_start = DateField()
    validity_end = DateField()
    currency = CharField(max_length=3)
    shipping_line_id = UUIDField(null=True, index=True)
    service_provider_id = UUIDField(null=True, index=True)
    spot_search_id = UUIDField(null=True, index=True)
    spot_search = IntegerField(default=0)
    checkout_id = UUIDField(null=True, index=True)
    checkout = IntegerField(default=0)
    shipment_id = UUIDField(null=True, index=True)
    shipment = IntegerField(default=0)
    disliked = IntegerField(default=0)
    liked = IntegerField(default=0)
    feedback_id = UUIDField(index=True)
    so1_select = IntegerField()
    so1_selected_rate_id = UUIDField()
    so1_selected_validity_id = UUIDField()
    source = CharField(null=True)
    selected_bas_standard_price = FloatField(default=0)
    standard_price_accuracy = FloatField(default=-sys.float_info.max)
    bas_standard_price_accuracy = FloatField(default=-sys.float_info.max)
    standard_price_diff_from_selected_rate = FloatField(default=0)
    bas_standard_price_diff_from_selected_rate = FloatField(default=0)
    fcl_freight_rate_statistic_id = BigIntegerField(default=0)
    selected_fcl_freight_rate_statistic_id = BigIntegerField(default=0)
    revenue_desk_visit = IntegerField(default=0)
    revenue_desk_select = IntegerField(default=0)
    given_priority = IntegerField(default=0)
    so1_visit = IntegerField(default=0)
    shipment_status = TextField(null=True)
    cancelled = IntegerField(default=0)
    completed = IntegerField(default=0)
    aborted = IntegerField(default=0)
    in_progress = IntegerField(default = 0)
    confirmed_by_importer_exporter = IntegerField(default=0)
    recieved = IntegerField(default=0)
    status = CharField(null=True, index=True)
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
