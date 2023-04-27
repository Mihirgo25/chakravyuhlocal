from peewee import *
from database.db_session import db
import datetime
from playhouse.postgres_ext import *
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from configs.fcl_freight_rate_constants import *
from fastapi import HTTPException
from configs.fcl_freight_rate_constants import CONTAINER_SIZES, CONTAINER_TYPES
from configs.definitions import FCL_FREIGHT_CURRENCIES ,FCL_FREIGHT_SEASONAL_CHARGES
from services.fcl_freight_rate.models.fcl_freight_rate_mapping import FclFreightRateMappings
from micro_services.client import *

LOCATION_TYPES = ('seaport', 'country', 'trade', 'continent')

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class FclFreightRateCommoditySurcharge(BaseModel):
    commodity = CharField(index=True, null=True)
    container_size = CharField(index=True, null=True)
    container_type = CharField(index=True, null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    currency = CharField(null=True)
    destination_continent_id = UUIDField(null=True)
    destination_country_id = UUIDField(null=True)
    destination_location_id = UUIDField(index=True, null=True)
    destination_location = BinaryJSONField(null=True)
    destination_location_type = CharField(null=True)
    destination_port_id = UUIDField(null=True)
    destination_trade_id = UUIDField(null=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    origin_continent_id = UUIDField(null=True)
    origin_country_id = UUIDField(null=True)
    origin_destination_location_type = CharField(null=True)
    origin_location_id = UUIDField(index=True, null=True)
    origin_location = BinaryJSONField(null=True)
    origin_location_type = CharField(null=True)
    origin_port_id = UUIDField(null=True)
    origin_trade_id = UUIDField(null=True)
    price = IntegerField(null=True)
    remarks = ArrayField(constraints=[SQL("DEFAULT '{}'::character varying[]")], field_class=CharField, null=True)
    service_provider_id = UUIDField(index=True, null=True)
    service_provider = BinaryJSONField(null=True)
    shipping_line_id = UUIDField(index=True, null=True)
    shipping_line = BinaryJSONField(null=True)
    updated_at = DateTimeField(default=datetime.datetime.now)
    sourced_by_id = UUIDField(null=True)
    sourced_by = BinaryJSONField(null=True)
    procured_by_id = UUIDField(null=True)
    procured_by = BinaryJSONField(null=True)
   
    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(FclFreightRateCommoditySurcharge, self).save(*args, **kwargs)

    class Meta:
        table_name = 'fcl_freight_rate_commodity_surcharges'

    def validate_location_types(self):
        locations = maps.list_locations({'filters':{'id': [str(self.origin_location_id), str(self.destination_location_id)]}})['list']
        for location in locations:
            if location['id']==str(self.origin_location_id):
                origin_location = location
                if origin_location.get('type') in LOCATION_TYPES:
                    self.origin_port_id = origin_location.get('id', None)
                    self.origin_country_id = origin_location.get('country_id', None)
                    self.origin_trade_id = origin_location.get('trade_id', None)
                    self.origin_continent_id = origin_location.get('continent_id', None)
                    self.origin_location_type = 'port' if origin_location.get('type') == 'seaport' else origin_location.get('type')
                    self.origin_location = {key:value for key,value in origin_location.items() if key in ['id','name','display_name','port_code','type']}
                else:
                    raise HTTPException(status_code=400, detail="Origin Location type not valid")
            elif location['id']==str(self.destination_location_id):
                destination_location = location
                if destination_location.get('type') in LOCATION_TYPES:
                    self.destination_port_id = destination_location.get('id', None)
                    self.destination_country_id = destination_location.get('country_id', None)
                    self.destination_trade_id = destination_location.get('trade_id', None)
                    self.destination_continent_id = destination_location.get('continent_id', None)
                    self.destination_location_type = 'port' if destination_location.get('type') == 'seaport' else destination_location.get('type')
                    self.destination_location = {key:value for key,value in destination_location.items() if key in ['id','name','display_name','port_code','type']}
                else:
                    raise HTTPException(status_code=400, detail="Destination Location type not valid")
            else:
                raise HTTPException(status_code=400,detail='Invalid Location')
    
    def set_origin_destination_location_type(self):
        try:
            self.origin_destination_location_type = ':'.join([self.origin_location_type,self.destination_location_type])
        except:
            self.origin_destination_location_type
    
    def validate_container_size(self):
        if self.container_size and self.container_size in CONTAINER_SIZES:
            return True
        return False
    
    def validate_container_type(self):
        if self.container_type and self.container_type in CONTAINER_TYPES:
            return True
        return False
    
    def validate_commodity(self):
      if self.container_type and self.commodity in FREIGHT_CONTAINER_COMMODITY_MAPPINGS[f"{self.container_type}"]:
        return True
      return False
    
    def validate_currency(self):
        fcl_freight_currencies = FCL_FREIGHT_CURRENCIES

        currencies = [currency for currency in fcl_freight_currencies]
        if self.currency and self.currency in currencies:
            return True
        return False
    

    def update_freight_objects(self):
        freight_query = FclFreightRate.select(FclFreightRate.id).where(
            (FclFreightRate.container_size == self.container_size),
            (FclFreightRate.container_type == 'standard'),
            (FclFreightRate.commodity == 'general') ,
            (FclFreightRate.shipping_line_id == self.shipping_line_id) ,
            (FclFreightRate.service_provider_id == self.service_provider_id) ,
            (FclFreightRate.importer_exporter_id == None) ,
            (getattr(FclFreightRate, str(f"origin_{self.origin_location_type}_id")) == self.origin_location_id) ,
            (getattr(FclFreightRate, str(f"destination_{self.destination_location_type}_id")) == self.destination_location_id)
        )
        for freight_id in freight_query:
            mapping = FclFreightRateMappings(fcl_freight_id=freight_id.id, object_type='FclFreightRateCommoditySurcharge', object_id=self.id)
            mapping.save()

    def detail(self):
        return {
            'seasonal_surcharge': {
                "id": self.id,
                "price": self.price,
                "currency": self.currency,
                "remarks": self.remarks
            }
        }
   
    def validate(self):
        self.validate_location_types()
        self.set_origin_destination_location_type()
        if not self.validate_container_size():
            raise HTTPException(status_code=400, detail="Container size not valid")
        if not self.validate_container_type():
            raise HTTPException(status_code=400, detail="Container type not valid")
        if not self.validate_commodity():
            raise HTTPException(status_code=400, detail="Commodity not valid")
        if not self.validate_currency():
            raise HTTPException(status_code=400, detail="Currency not valid")
        return True
