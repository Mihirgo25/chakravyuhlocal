from peewee import (
    Model,
    UUIDField,
    FloatField,
    CharField,
    TextField,
    DateField,
    IntegerField,
)
from datetime import datetime
from database.db_session import db
from playhouse.postgres_ext import DateTimeTZField, BigAutoField
from services.bramhastra.enums import ImportTypes


class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True


class FclFreightRateStatistic(BaseModel):
    id = BigAutoField(primary_key=True)
    identifier = TextField(index=True)
    validity_id = UUIDField(index=True)
    rate_id = UUIDField(index=True)
    payment_term = CharField()
    schedule_type = CharField()
    origin_port_id = UUIDField(index=True)
    destination_port_id = UUIDField(index=True)
    origin_main_port_id = UUIDField(null=True, index=True)
    destination_main_port_id = UUIDField(null=True, index=True)
    origin_region_id = UUIDField(null=True)
    destination_region_id = UUIDField(null=True)
    origin_country_id = UUIDField(null=True)
    destination_country_id = UUIDField(null=True)
    origin_continent_id = UUIDField(null=True)
    destination_continent_id = UUIDField(null=True)
    origin_trade_id = UUIDField(null=True)
    destination_trade_id = UUIDField(null=True)
    origin_pricing_zone_map_id = UUIDField(null=True)
    destination_pricing_zone_map_id = UUIDField(null=True)
    price = FloatField()
    standard_price = FloatField()
    market_price = FloatField()
    validity_start = DateField()
    validity_end = DateField()
    currency = CharField(max_length=3)
    shipping_line_id = UUIDField(null=True, index=True)
    service_provider_id = UUIDField(null=True, index=True)
    accuracy = FloatField(default=-1.0)
    mode = CharField(index=True)
    likes_count = IntegerField(default=0)
    dislikes_count = IntegerField(default=0)
    feedback_recieved_count = IntegerField(default=0)
    dislikes_rate_reverted_count = IntegerField(default=0)
    spot_search_count = IntegerField(default=0)
    buy_quotations_created = IntegerField(default=0)
    sell_quotations_created = IntegerField(default=0)
    checkout_count = IntegerField(default=0)
    bookings_created = IntegerField(default=0)
    rate_created_at = DateTimeTZField()
    rate_updated_at = DateTimeTZField()
    validity_created_at = DateTimeTZField(default=datetime.utcnow())
    validity_updated_at = DateTimeTZField(default=datetime.utcnow())
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
    cogo_entity_id = UUIDField(null=True, index=True)
    rate_type = CharField()
    sourced_by_id = UUIDField(null=True)
    procured_by_id = UUIDField(null=True)
    shipment_aborted_count = IntegerField(default=0)
    shipment_cancelled_count = IntegerField(default=0)
    shipment_completed_count = IntegerField(default=0)
    shipment_confirmed_by_importer_exporter_count = IntegerField(default=0)
    shipment_in_progress_count = IntegerField(default=0)
    shipment_received_count = IntegerField(default=0)
    shipment_awaited_service_provider_confirmation_count = IntegerField(default=0)
    shipment_init_count = IntegerField(default=0)
    shipment_containers_gated_in_count = IntegerField(default=0)
    shipment_containers_gated_out_count = IntegerField(default=0)
    shipment_vessel_arrived_count = IntegerField(default=0)
    shipment_is_active_count = IntegerField(default=0)
    shipment_booking_rate_is_too_low_count = IntegerField(default=0)
    revenue_desk_visit_count = IntegerField(default=0)
    so1_visit_count = IntegerField(default=0)
    created_at = DateTimeTZField(default=datetime.utcnow())
    updated_at = DateTimeTZField(default=datetime.utcnow(), index=True)
    version = IntegerField(default=1, index=True)
    sign = IntegerField(default=1)
    status = CharField(default="active")
    last_action = CharField(default="create")
    rate_deviation_from_booking_rate = FloatField(default=0)
    rate_deviation_from_cluster_base_rate = FloatField(default=0)
    rate_deviation_from_booking_on_cluster_base_rate = FloatField(default=0)
    rate_deviation_from_latest_booking = FloatField(default=0)
    rate_deviation_from_reverted_rate = FloatField(default=0)
    last_indicative_rate = FloatField(default=0)
    average_booking_rate = FloatField(default=0)
    booking_rate_count = FloatField(default=0)
    parent_rate_id = UUIDField(null=True, index=True)
    parent_validity_id = UUIDField(null=True, index=True)
    so1_select_count = IntegerField(default=0)
    total_priority = IntegerField(default=0)
    parent_mode = CharField(null=True, index=True)
    source = CharField(null=True)
    source_id = UUIDField(null=True, index=True)
    performed_by_id = UUIDField(null=True, index=True)
    performed_by_type = CharField(null=True, index=True)
    rate_sheet_id = UUIDField(null=True, index=True)
    bulk_operation_id = UUIDField(null=True, index=True)
    operation_created_at = DateTimeTZField(default=datetime.utcnow())
    operation_updated_at = DateTimeTZField(default=datetime.utcnow(), index=True)

    def save(self, *args, **kwargs):
        self.operation_updated_at = datetime.utcnow()
        return super(FclFreightRateStatistic, self).save(*args, **kwargs)

    def update_force(self, params):
        for k, v in params.items():
            setattr(self, k, v)
        self.save()

    def refresh(self):
        return type(self).get(self._pk_expr())

    CLICK_KEYS = [
        "origin_continent_id",
        "origin_country_id",
        "origin_port_id",
        "rate_id",
        "validity_id",
    ]

    IMPORT_TYPE = ImportTypes.csv.value

    class Meta:
        table_name = "fcl_freight_rate_statistics"
