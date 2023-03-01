from peewee import * 
from database.db_session import db
from playhouse.postgres_ext import *
import datetime


class BaseModel(Model):
    class Meta:
        database = db

class FclFreightRateSeasonalSurcharge(BaseModel):
    code = CharField(null=True)
    container_size = CharField(null=True)
    container_type = CharField(index=True, null=True)
    created_at = DateTimeField(default=datetime.datetime.now())
    currency = CharField(null=True)
    destination_continent_id = UUIDField(index=True, null=True)
    destination_country_id = UUIDField(index=True, null=True)
    destination_location_id = UUIDField(null=True)
    destination_location_type = CharField(null=True)
    destination_port_id = UUIDField(index=True, null=True)
    destination_trade_id = UUIDField(index=True, null=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    origin_continent_id = UUIDField(index=True, null=True)
    origin_country_id = UUIDField(index=True, null=True)
    origin_destination_location_type = CharField(null=True)
    origin_location_id = UUIDField(null=True)
    origin_location_type = CharField(null=True)
    origin_port_id = UUIDField(index=True, null=True)
    origin_trade_id = UUIDField(index=True, null=True)
    price = IntegerField(null=True)
    remarks = ArrayField(constraints=[SQL("DEFAULT '{}'::character varying[]")], field_class=CharField, null=True)
    service_provider_id = UUIDField(null=True)
    shipping_line_id = UUIDField(index=True, null=True)
    updated_at = DateTimeField(default=datetime.datetime.now())
    validity_end = DateField(index=True, null=True)
    validity_start = DateField(null=True)

    class Meta:
        table_name = 'fcl_freight_rate_seasonal_surcharges'
        indexes = (
            (('container_size', 'container_type'), False),
            (('origin_location_id', 'destination_location_id', 'container_size', 'container_type', 'shipping_line_id', 'service_provider_id', 'code'), True),
            (('service_provider_id', 'shipping_line_id', 'container_size', 'container_type', 'code'), False),
            (('updated_at', 'id', 'service_provider_id'), False),
            (('updated_at', 'service_provider_id'), False),
            (('updated_at', 'service_provider_id', 'code'), False),
            (('updated_at', 'service_provider_id', 'shipping_line_id', 'code'), False),
            (('validity_start', 'validity_end'), False),
        )