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
    selected_air_freight_rate_statistic_id = UUIDField(null=True, index=True, default=DEFAULT_UUID)
    origin_airport_id = UUIDField(null=True, index=True, default=DEFAULT_UUID)
    destination_airport_id = UUIDField(null=True, index=True, default=DEFAULT_UUID)
    origin_country_id = UUIDField(null=True, index=True, default=DEFAULT_UUID)
    destination_country_id = UUIDField(null=True, index=True, default=DEFAULT_UUID)
    origin_continent_id = UUIDField(null=True, index=True, default=DEFAULT_UUID)
    destination_continent_id = UUIDField(null=True, index=True, default=DEFAULT_UUID)
    origin_region_id = UUIDField(null=True, index=True, default=DEFAULT_UUID)
    destination_region_id = UUIDField(null=True, index=True, default=DEFAULT_UUID)
    origin_trade_id = UUIDField(null=True, index=True, default=DEFAULT_UUID)
    destination_trade_id = UUIDField(null=True, index=True, default=DEFAULT_UUID)
    commodity = CharField(null=True,index=True)
    commodity_type = CharField(null=True)
    commodity_subtype = CharField(null=True)
    operation_type = TextField()
    stacking_type = TextField()
    shipment_type = TextField()
    spot_search_id = UUIDField(null=True, index=True, default=DEFAULT_UUID)
    spot_search_air_freight_service_id = UUIDField(null=True, index=True, default=DEFAULT_UUID)
    container_size = TextField(null=True, index=True)
    container_type = TextField(null=True, index=True)
    service_provider_id = UUIDField(null=True, index=True, default=DEFAULT_UUID)
    rate_id = UUIDField(index=True, default=DEFAULT_UUID)
    validity_id = UUIDField(index=True, default=DEFAULT_UUID)
    mode = TextField()
    parent_mode = TextField(index=True)
    parent_rate_mode = TextField()
    standard_price = FloatField(default=0, null=True)
    price = FloatField(default=0, null=True)
    currency = CharField(max_length=3, null=True)
    market_price = FloatField(default=0, null=True)
    validity_start = DateField(null=True)
    validity_end = DateField(null=True)
    airline_id = UUIDField(null=True, index=True, default=DEFAULT_UUID)
    selected_standard_price = FloatField(default=0, null=True)
    standard_price_accuracy = FloatField(default=0, null=True) 
    standard_price_diff_from_selected_rate = FloatField(default=0, null=True)
    revenue_desk_state = TextField(default= None)
    shipment_service_id = UUIDField(null=True, index=True, default=DEFAULT_UUID)
    shipment_state = TextField(default=None)
    shipment_cancellation_reason = TextField(default=None)
    feedback_id = UUIDField(null=True, index=True)
    feedback_state = TextField(null=True, index=True)
    feedback_type = TextField()
    feedback_ids = ArrayField(UUIDField())
    rate_requested_ids = ArrayField(UUIDField)
    rate_requested_state = TextField()
    selected_type = TextField(null=True, default="")
    given_priority = IntegerField(default=0, null=True)
    rate_created_at = DateTimeTZField(index=True, null=True)
    rate_updated_at = DateTimeTZField(index=True, null=True)
    validity_created_at = DateTimeTZField(index=True, null=True)
    validity_updated_at = DateTimeTZField(index=True, null=True)
    created_at = DateTimeTZField(index=True, default=datetime.now())
    updated_at = DateTimeTZField(index=True, default=datetime.now())
    operation_created_at = DateTimeTZField(default=datetime.now())
    operation_updated_at = DateTimeTZField(default=datetime.now(), index=True)
    sign = IntegerField(default=1)
    version = IntegerField(default=1)

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
