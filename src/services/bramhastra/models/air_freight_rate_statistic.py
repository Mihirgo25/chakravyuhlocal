from peewee import Model, UUIDField, FloatField, BigIntegerField, CharField, TextField, DateField,IntegerField
from datetime import datetime
from database.db_session import db
from playhouse.postgres_ext import DateTimeTZField


class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True


class AirFreightRateStatistic(BaseModel):
    id = BigIntegerField(sequence='air_freight_rate_stats_seq')
    identifier = TextField()
    validity_id = UUIDField()
    rate_id = UUIDField()
    origin_airport_id = UUIDField(null=True)
    destination_airport_id = UUIDField(null=True)
    origin_country_id = UUIDField(null=True)
    destination_country_id = UUIDField(null=True)
    origin_continent_id = UUIDField(null=True)
    destination_continent_id = UUIDField(null=True)
    origin_region_id = UUIDField(null=True)
    destination_region_id = UUIDField(null=True)
    origin_trade_id = UUIDField(null=True)
    destination_trade_id = UUIDField(null=True)
    origin_pricing_zone_map_id = UUIDField(null=True)
    destination_pricing_zone_map_id = UUIDField(null=True)
    price = FloatField(null=True)
    standard_price = FloatField(null=True)
    lower_limit = FloatField()
    upper_limit = FloatField()
    currency = CharField(max_length=3)
    validity_start = DateField()
    validity_end = DateField()
    density_category = CharField(null=True)
    max_density_weight = FloatField(null=True)
    min_density_weight = FloatField(null=True)
    airline_id = UUIDField(null=True)
    service_provider_id = UUIDField(null=True)
    accuracy = FloatField(default=-1.0)
    source = CharField(null=True)
    likes_count = IntegerField(default=0)
    dislikes_count = IntegerField(default=0)
    feedback_recieved_count = IntegerField(default=0),
    dislikes_rate_reverted_count = IntegerField(default=0),
    spot_search_count = IntegerField(default=0)
    buy_quotations_created = IntegerField(default=0)
    sell_quotations_created = IntegerField(default=0)
    checkout_count = IntegerField(default=0)
    bookings_created = IntegerField(default=0)
    rate_created_at = DateTimeTZField()
    rate_updated_at = DateTimeTZField()
    validity_created_at = DateTimeTZField(default = datetime.utcnow())
    validity_updated_at = DateTimeTZField(default = datetime.utcnow())
    commodity = CharField(null=True)
    commodity_type = CharField(null=True)
    commodity_sub_type = CharField(null=True)
    operation_type = CharField(null=True)
    shipment_type = CharField(null=True)
    stacking_type = CharField(null=True)
    origin_local_id = UUIDField(null=True)
    destination_local_id = UUIDField(null=True)
    surcharge_id = UUIDField(null=True)
    cogo_entity_id = UUIDField(null=True)
    price_type = CharField(null=True)
    rate_type = CharField(null=True)
    sourced_by_id = UUIDField(null=True)
    procured_by_id = UUIDField(null=True)
    shipment_aborted_count = IntegerField(default=0)
    shipment_cancelled_count = IntegerField(default=0) 
    shipment_completed_count = IntegerField(default=0) 
    shipment_is_active_count = IntegerField(default=0)
    shipment_received_count = IntegerField(default=0)
    shipment_confirmed_by_importer_exporter_count = IntegerField(default=0)
    shipment_confirmed_by_service_provider_count = IntegerField(default=0)
    shipment_awaited_service_provider_confirmation_count = IntegerField(default=0)
    shipment_init_count = IntegerField(default=0)
    shipment_flight_arrived_count = IntegerField(default=0)
    shipment_flight_departed_count = IntegerField(default=0)
    shipment_cargo_handed_over_at_destination_count = IntegerField(default=0)
    shipment_cargo_handed_over_at_origin_count = IntegerField(default=0)
    created_at = DateTimeTZField(default = datetime.utcnow())
    updated_at = DateTimeTZField(default = datetime.utcnow())
    version = IntegerField(default=1)
    sign = IntegerField(default=1)
    revenue_desk_visit_count = IntegerField(default=0)
    so1_visit_count = IntegerField(default=0)
    status = CharField(default = 'active')
    last_action = CharField(default = 'create')
    rate_deviation_from_booking_rate = FloatField(default=0)
    rate_deviation_from_cluster_base_rate = FloatField(default=0)
    rate_deviation_from_booking_on_cluster_base_rate = FloatField(default=0)
    rate_deviation_from_latest_booking = FloatField(default=0)
    booking_rate_count=FloatField(default=0)
    average_booking_rate = FloatField(default=-1)
    parent_rate_id = UUIDField(null=True)


    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        self.validity_updated_at = datetime.utcnow()
        return super(AirFreightRateStatistic, self).save(*args, **kwargs)

    def update_force(self, params):
        for k, v in params.items():
            setattr(self, k, v)
        self.save()

    class Meta:
        table_name = "air_freight_rate_statistics"
