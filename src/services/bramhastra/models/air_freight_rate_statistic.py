from peewee import (
    Model,
    UUIDField,
    FloatField,
    CharField,
    TextField,
    DateField,
    IntegerField,
    BooleanField,
    BigAutoField,
)
from datetime import datetime
from database.db_session import db
from playhouse.postgres_ext import DateTimeTZField
from configs.env import DEFAULT_USER_ID
from services.bramhastra.enums import ImportTypes


class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True


class AirFreightRateStatistic(BaseModel):
    id = BigAutoField(primary_key=True)
    identifier = TextField(index=True)
    validity_id = UUIDField(index=True)
    rate_id = UUIDField(index=True)
    origin_airport_id = UUIDField(null=True, index=True)
    destination_airport_id = UUIDField(null=True, index=True)
    origin_country_id = UUIDField(null=True, index=True)
    destination_country_id = UUIDField(null=True, index=True)
    origin_continent_id = UUIDField(null=True, index=True)
    destination_continent_id = UUIDField(null=True, index=True)
    origin_region_id = UUIDField(null=True)
    destination_region_id = UUIDField(null=True)
    origin_trade_id = UUIDField(null=True)
    destination_trade_id = UUIDField(null=True)
    origin_pricing_zone_map_id = UUIDField(null=True, index=True)
    destination_pricing_zone_map_id = UUIDField(null=True, index=True)
    price = FloatField(default=0)
    lower_limit = FloatField()
    upper_limit = FloatField()
    standard_price = FloatField(default=0)
    currency = CharField(max_length=3)
    validity_start = DateField()
    validity_end = DateField()
    density_category = CharField(null=True)
    max_density_weight = FloatField(null=True)
    min_density_weight = FloatField(null=True)
    airline_id = UUIDField(null=True, index=True)
    service_provider_id = UUIDField(null=True, index=True)
    accuracy = FloatField(default=-1.0)
    source = CharField(null=True)
    likes_count = IntegerField(default=0)
    dislikes_count = IntegerField(default=0)
    feedback_recieved_count = (IntegerField(default=0))
    dislikes_rate_reverted_count = (IntegerField(default=0))
    spot_search_count = IntegerField(default=0)
    buy_quotations_created = IntegerField(default=0)
    sell_quotations_created = IntegerField(default=0)
    checkout_count = IntegerField(default=0)
    bookings_created = IntegerField(default=0)
    rate_created_at = DateTimeTZField(index=True)
    rate_updated_at = DateTimeTZField(index=True)
    validity_created_at = DateTimeTZField(default=datetime.utcnow())
    validity_updated_at = DateTimeTZField(default=datetime.utcnow(), index=True)
    commodity = CharField(null=True)
    commodity_type = CharField(null=True)
    commodity_sub_type = CharField(null=True)
    operation_type = CharField(null=True)
    shipment_type = CharField(null=True)
    stacking_type = CharField(null=True)
    origin_local_id = UUIDField(null=True)
    destination_local_id = UUIDField(null=True)
    surcharge_id = UUIDField(null=True)
    cogo_entity_id = UUIDField(null=True, index=True)
    price_type = CharField(null=True)
    rate_type = CharField(null=True, index=True)
    sourced_by_id = UUIDField(null=True, index=True)
    procured_by_id = UUIDField(null=True, index=True)
    created_at = DateTimeTZField(default=datetime.utcnow())
    updated_at = DateTimeTZField(default=datetime.utcnow(), index=True)
    version = IntegerField(default=1)
    sign = IntegerField(default=1)
    status = CharField(default="active")
    last_action = CharField(default="create")
    rate_deviation_from_booking_rate = FloatField(default=0)
    rate_deviation_from_booking_on_cluster_base_rate = FloatField(default=0)
    rate_deviation_from_latest_booking = FloatField(default=0)
    average_booking_rate = FloatField(default=-1)
    parent_rate_id = UUIDField(null=True, index=True)
    booking_rate_count = FloatField(default=0)
    parent_validity_id = UUIDField(null=True, index=True)
    height = FloatField(default=0)
    breadth = FloatField(default=0)
    length = FloatField(default=0)
    maximum_weight = FloatField(default=0)
    flight_uuid = UUIDField(index=True, null=True)
    rate_deviation_from_cluster_base_rate = FloatField(default=0)
    performed_by_id = UUIDField(index = True,default = DEFAULT_USER_ID, null = True)
    performed_by_type = CharField(default = "agent",null = True)
    operation_created_at = DateTimeTZField(default = datetime.utcnow())
    operation_updated_at = DateTimeTZField(default = datetime.utcnow())
    is_deleted = BooleanField(index = True,default = False)
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        self.validity_updated_at = datetime.utcnow()
        return super(AirFreightRateStatistic, self).save(*args, **kwargs)

    def update_force(self, params):
        for k, v in params.items():
            setattr(self, k, v)
        self.save()
        
    CLICK_KEYS = [
        "origin_continent_id",
        "origin_country_id",
        "origin_airport_id",
        "rate_id",
        "validity_id",
    ]

    IMPORT_TYPE = ImportTypes.csv.value

    class Meta:
        table_name = "air_freight_rate_statistics"
