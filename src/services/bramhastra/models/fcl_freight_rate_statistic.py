from peewee import Model, BigAutoField, UUIDField, FloatField, IntegerField, CharField
import datetime
from database.db_session import db
from playhouse.postgres_ext import DateTimeTZField, ArrayField, BinaryJSONField


class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True


class FclFreightRateStatistic(BaseModel):
    id = BigAutoField()
    validity_id = UUIDField()
    rate_id = UUIDField()
    origin_port_id = UUIDField(null=True)
    destination_port_id = UUIDField(null=True)
    origin_main_port_id = UUIDField(null=True)
    destination_main_port_id = UUIDField(null=True)
    origin_country_id = UUIDField(null=True)
    destination_country_id = UUIDField(null=True)
    origin_region_id = UUIDField(null=True)
    destination_region_id = UUIDField(null=True)
    origin_country_id = UUIDField(null=True)
    destination_country_id = UUIDField(null=True)
    origin_trade_id = UUIDField(null=True)
    destination_trade_id = UUIDField(null=True)
    origin_pricing_zone_map_id = UUIDField(null=True)
    destination_pricing_zone_map_id = UUIDField(null=True)
    price = FloatField()
    currency = CharField(max_length=3)
    line_items = BinaryJSONField()
    shipping_line_id = UUIDField(null=True)
    service_provider_id = UUIDField(null=True)
    accuracy = FloatField()
    source = CharField()
    mode = CharField()
    likes_count = IntegerField()
    dislikes_count = IntegerField()
    spot_search_count = IntegerField()
    quotations_created = IntegerField()
    checkout_count = IntegerField()
    bookings_created = IntegerField()
    rate_created_at = DateTimeTZField()
    rate_updated_at = DateTimeTZField()
    validity_created_at = DateTimeTZField()
    validity_updated_at = DateTimeTZField()
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
    destintination_demurrage_id = UUIDField(null=True)
    cogo_entity_id = UUIDField(null=True)
    rate_type = CharField()
    tags = ArrayField(CharField, null=True)
    slabs = BinaryJSONField()
    free_limit = IntegerField()
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
    created_at = DateTimeTZField()
    updated_at = DateTimeTZField()
    status = CharField()

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(FclFreightRateStatistic, self).save(*args, **kwargs)

    class Meta:
        table_name = "fcl_freight_rate_statistics"
