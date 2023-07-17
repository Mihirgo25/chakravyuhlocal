from peewee import Model, BigAutoField, UUIDField, FloatField, IntegerField, CharField, TextField, DateField
from datetime import datetime
from database.db_session import db
from playhouse.postgres_ext import DateTimeTZField, ArrayField, BinaryJSONField


class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True


class FclFreightRateStatistic(BaseModel):
    id = BigAutoField()
    identifier = TextField()
    validity_id = UUIDField()
    rate_id = UUIDField()
    payment_term = CharField()
    schedule_type = CharField()
    origin_port_id = UUIDField(null=True)
    destination_port_id = UUIDField(null=True)
    origin_main_port_id = UUIDField(null=True)
    destination_main_port_id = UUIDField(null=True)
    origin_region_id = UUIDField(null=True)
    destination_region_id = UUIDField(null=True)
    origin_country_id = UUIDField(null=True)
    destination_country_id = UUIDField(null=True)
    origin_trade_id = UUIDField(null=True)
    destination_trade_id = UUIDField(null=True)
    origin_pricing_zone_map_id = UUIDField(null=True)
    destination_pricing_zone_map_id = UUIDField(null=True)
    price = FloatField()
    market_price = FloatField()
    validity_start = DateField()
    validity_end = DateField()
    currency = CharField(max_length=3)
    line_items = BinaryJSONField()
    shipping_line_id = UUIDField(null=True)
    service_provider_id = UUIDField(null=True)
    accuracy = FloatField(default=-1.0)
    mode = CharField()
    likes_count = IntegerField(default=0)
    dislikes_count = IntegerField(default=0)
    spot_search_count = IntegerField(default=0)
    buy_quotations_created = IntegerField(default=0)
    sell_quotations_created = IntegerField(default=0)
    checkout_count = IntegerField(default=0)
    bookings_created = IntegerField(default=0)
    rate_created_at = DateTimeTZField()
    rate_updated_at = DateTimeTZField()
    validity_created_at = DateTimeTZField(default = datetime.utcnow())
    validity_updated_at = DateTimeTZField(default = datetime.utcnow())
    commodity = CharField()
    container_size = CharField(max_length=10)
    container_type = CharField()
    containers_count = IntegerField(default=0)
    origin_local_id = UUIDField(null=True)
    destination_local_id = UUIDField(null=True)
    applicable_origin_local_count = IntegerField(default=0)
    applicable_destination_local_count = IntegerField(default=0)
    origin_detention_id = UUIDField(null=True)
    destination_detention_id = UUIDField(null=True)
    origin_demurrage_id = UUIDField(null=True)
    destination_demurrage_id = UUIDField(null=True)
    cogo_entity_id = UUIDField(null=True)
    rate_type = CharField()
    slabs = BinaryJSONField(null = True)
    sourced_by_id = UUIDField(null=True)
    procured_by_id = UUIDField(null=True)
    shipment_aborted_count = IntegerField(default=0)
    shipment_cancelled_count = IntegerField(default=0)
    shipment_completed_count = IntegerField(default=0)
    shipment_confirmed_by_service_provider_countb = IntegerField(default=0)
    shipment_awaited_service_provider_confirmation_count = IntegerField(default=0)
    shipment_init_count = IntegerField(default=0)
    shipment_containers_gated_in_count = IntegerField(default=0)
    shipment_containers_gated_out_count = IntegerField(default=0)
    shipment_vessel_arrived_count = IntegerField(default=0)
    shipment_is_active_count = IntegerField(default=0)
    shipment_cancellation_reason_got_a_cheaper_rate_from_my_service_provider_count = (
        IntegerField(default=0)
    )
    shipment_booking_rate_is_too_low_count = IntegerField(default=0)
    average_booking_rate = FloatField(default=-1.0)
    created_at = DateTimeTZField(default = datetime.utcnow())
    updated_at = DateTimeTZField(default = datetime.utcnow())
    version = IntegerField(default=1)
    state = IntegerField(default=1)
    status = CharField(default = 'active')
    last_action = CharField(default = 'create')

    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        self.validity_updated_at = datetime.utcnow()
        return super(FclFreightRateStatistic, self).save(*args, **kwargs)

    class Meta:
        table_name = "fcl_freight_rate_statistics"
