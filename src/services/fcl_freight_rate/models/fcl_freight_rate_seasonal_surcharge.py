from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
import datetime
import yaml
from rails_client import client
from fastapi import HTTPException
from configs.fcl_freight_rate_constants import CONTAINER_SIZES, CONTAINER_TYPES
from configs.defintions import FCL_FREIGHT_SEASONAL_CHARGES

LOCATION_TYPES = ('seaport', 'country', 'trade', 'continent')

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = db

class Mapping(Model):
    fcl_freight_id = ForeignKeyField(FclFreightRate, backref='mappings')

def to_dict(obj):
    return json.loads(json.dumps(obj, default=lambda o: o.__dict__))

class FclFreightRateSeasonalSurcharge(BaseModel):
    code = CharField(null=True)
    container_size = CharField(null=True)
    container_type = CharField(index=True, null=True)
    created_at = DateTimeField()
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
    updated_at = DateTimeField()
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

    def validate_origin_location(self):
        origin_location = client.ruby.list_locations({'filters':{'id': self.origin_location_id}})['list'][0]
        if origin_location.get('type') in LOCATION_TYPES:
            self.origin_port_id = origin_location.get('id', None)
            self.origin_country_id = origin_location.get('country_id', None)
            self.origin_trade_id = origin_location.get('trade_id', None)
            self.origin_continent_id = origin_location.get('continent_id', None)
            self.origin_location_type = 'port' if origin_location.get('type') == 'seaport' else origin_location.get('type')
            return True
        return False

    def validate_destination_location(self):
        destination_location = client.ruby.list_locations({'filters':{'id': self.destination_location_id}})['list'][0]
        if destination_location.get('type') in LOCATION_TYPES:
            self.destination_port_id = destination_location.get('id', None)
            self.destination_country_id = destination_location.get('country_id', None)
            self.destination_trade_id = destination_location.get('trade_id', None)
            self.destination_continent_id = destination_location.get('continent_id', None)
            self.destination_location_type = 'port' if destination_location.get('type') == 'seaport' else destination_location.get('type')
            self.origin_destination_location_type = str(self.origin_location_type) + ':' + str(self.destination_location_type)
            return True
        return False

    def validate_shipping_line(self):
        shipping_line = client.ruby.list_operators({'filters':{'id': self.shipping_line_id}})['list'][0]
        if shipping_line.get('operator_type') == 'shipping_line':
            return True
        return False

    def validate_service_provider(self):
        service_provider = client.ruby.list_organizations({'filters':{'id': self.service_provider_id}})['list'][0]
        if service_provider.get('operator_type') == 'service_provider':
            return True
        return False

    def validate_container_size(self):
        if self.container_size and self.container_size in CONTAINER_SIZES:
            return True
        return False

    def validate_container_type(self):
        if self.container_type and self.container_type in CONTAINER_TYPES:
            return True
        return False
    
    def validate_code(self):
        with open(FCL_FREIGHT_SEASONAL_CHARGES, 'r') as file:
            fcl_freight_seasonal_charges = yaml.safe_load(file)

        if self.code and self.code in fcl_freight_seasonal_charges:
            return True
        return False
    
    def validate_validity(self):
        if self.validity_start and self.validity_end:
            if self.validity_start > self.validity_end:
                raise HTTPException(status_code=499, detail="Validity start date should be less than validity end date")

    def valid_uniqueness(self):
        freight_seasonal_surcharge_cnt = FclFreightRateSeasonalSurcharge.select().where(
            FclFreightRateSeasonalSurcharge.origin_location_id == self.origin_location_id,
            FclFreightRateSeasonalSurcharge.destination_location_id == self.destination_location_id,
            FclFreightRateSeasonalSurcharge.container_size == self.container_size,
            FclFreightRateSeasonalSurcharge.container_type == self.container_type,
            FclFreightRateSeasonalSurcharge.shipping_line_id == self.shipping_line_id,
            FclFreightRateSeasonalSurcharge.service_provider_id == self.service_provider_id
        ).count()

        if self.id and freight_seasonal_surcharge_cnt==1:
            return True
        if not self.id and freight_seasonal_surcharge_cnt==0:
            return True
        return False
    
    def is_active(self):
        if self.validity_start and self.validity_end:
            if datetime.date.today() < self.validity_end:
                return True
        return False

    def update_freight_objects(self):
        freight_query = FclFreightRate.select().where(
            (FclFreightRate.container_size == self.container_size) &
            (FclFreightRate.container_type == self.container_type) &
            (FclFreightRate.shipping_line_id == self.shipping_line_id) &
            (FclFreightRate.service_provider_id == self.service_provider_id) &
            (getattr(FclFreightRate, f"origin_{self.origin_location_type}_id") == self.origin_location_id) &
            (getattr(FclFreightRate, f"destination_{self.destination_location_type}_id") == self.destination_location_id)
        )
        for freight_id in freight_query.select(FclFreightRate.id):
            mapping = Mapping(fcl_freight_id=freight_id.id)
            mapping.save()

    def detail(self):
        return {
            'seasonal_surcharge': self.as_dict(only=[
                'id',
                'validity_start',
                'validity_end',
                'price',
                'currency',
                'remarks'
            ])
        }

    def save(self, *args, **kwargs):
        self.validate_origin_location()
        self.validate_destination_location()
        self.validate_shipping_line()
        self.validate_service_provider()
        self.validate_container_size()
        self.validate_container_type()
        self.validate_code()
        self.validate_validity()
        if not self.valid_uniqueness():
            raise HTTPException(status_code=499, detail="Duplicate entry")
        super().save(*args, **kwargs)
        self.update_freight_objects()

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