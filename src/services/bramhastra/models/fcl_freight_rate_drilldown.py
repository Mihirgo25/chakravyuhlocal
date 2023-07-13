from peewee import Model, BigAutoField, UUIDField, CharField, IntegerField
import datetime
from database.db_session import db
from playhouse.postgres_ext import DateTimeTZField, BinaryJSONField


class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True


class FclFreightRateDrillDown(BaseModel):
    id = BigAutoField()
    clickhouse_id = IntegerField(default=0)
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
    origin_pricing_zone_map_id = UUIDField(null=True)
    destination_pricing_zone_map_id = UUIDField(null=True)
    shipping_line_id = UUIDField(null=True)
    service_provider_id = UUIDField(null=True)
    spot_search_id = UUIDField(null=True)
    spot_search_fcl_freight_rate_services_id = UUIDField(null=True)
    spot_search_created_at = DateTimeTZField(null = True)
    checkout_id = UUIDField(null=True)
    checkout_fcl_freight_rate_services_id = UUIDField(null=True)
    checkout_services = BinaryJSONField()
    checkout_created_at = DateTimeTZField()
    shipment_id = UUIDField(null=True)
    shipment_fcl_freight_rate_services_id = UUIDField(null=True)
    shipment_cancellation_reason = CharField(default = '')
    shipment_state = CharField()
    shipment_is_active = CharField()
    shipment_created_at = DateTimeTZField()
    shipment_updated_at = DateTimeTZField()
    created_at = DateTimeTZField()
    updated_at = DateTimeTZField()
    status = CharField()

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(FclFreightRateDrillDown, self).save(*args, **kwargs)

    class Meta:
        table_name = "fcl_freight_rate_drill_down"
