from peewee import *
from database.db_session import db
import uuid
import datetime
from playhouse.postgres_ext import BinaryJSONField, ArrayField
from fastapi import HTTPException
from micro_services.client import *
from params import LineItem
from services.haulage_freight_rate.interactions.update_haulage_freight_rate_platform_prices import update_haulage_rate_platform_prices
from configs.definitions import HAULAGE_FREIGHT_CHARGES
from configs.global_constants import *
from configs.haulage_freight_rate_constants import *
from database.rails_db import *



class BaseModel(Model):
    class Meta:
        database = db
class HaulageFreightRate(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    origin_location_id = UUIDField(null=True)
    origin_cluster_id = UUIDField(null=True)
    origin_city_id = UUIDField(null=True)
    destination_location_id = UUIDField(null=True)
    destination_cluster_id = UUIDField(null=True)
    destination_city_id = UUIDField(null=True)
    container_size = CharField(index=True, null=True)
    commodity_type = CharField(index=True, null=True)
    commodity = CharField(index=True, null=True)
    importer_exporter_id = UUIDField(null=True)
    service_provider_id = UUIDField(null=True)
    containers_count =  IntegerField(index=True, null=True)
    container_type = CharField(index=True, null=True)
    weight_slabs = BinaryJSONField(index=True, null=True)
    line_items = BinaryJSONField(index=True, null=True)
    is_line_items_error_messages_present = BooleanField(index=True, null=True)
    is_line_items_info_messages_present = BooleanField(index=True, null=True)
    line_items_error_messages = BinaryJSONField(index=True, null=True)
    line_items_info_messages = BinaryJSONField(index=True, null=True)
    rate_not_available_entry = BooleanField(index=True, null=True)
    trip_type = CharField(index=True, null=True)
    validity_start = DateTimeField(default=datetime.datetime.now)
    validity_end = DateTimeField(default = datetime.datetime.now() - datetime.timedelta(30))
    detention_free_time = IntegerField(index=True, null=True)
    transit_time = IntegerField(index=True, null=True)
    haulage_type = CharField(index=True, null=True, default='merchant')
    transport_modes =ArrayField(CharField, null=True)
    destination_country_id = UUIDField(null=True)
    transport_modes_keyword = CharField(index=True, null=True)
    distance = FloatField(null=True, index=True)
    origin_country_id = UUIDField(null=True)
    shipping_line_id = UUIDField(null=True)
    origin_destination_location_type = CharField(index=True, null=True)
    destination_location_type = CharField(index=True, null=True)
    origin_location_type = CharField(index=True, null=True)
    origin_location_ids = ArrayField(UUIDField, null=True)
    destination_location_ids = ArrayField(UUIDField, null=True)
    importer_exporter = BinaryJSONField(index=True, null=True)
    service_provider = BinaryJSONField(index=True, null=True)
    origin_location = BinaryJSONField(index=True, null=True)
    destination_location = BinaryJSONField(index=True, null=True)
    shipping_line = BinaryJSONField(index=True, null=True)
    validities = BinaryJSONField(default = [], null=True)
    created_at = DateTimeField(default=datetime.datetime.now, index=True)
    updated_at = DateTimeField(default=datetime.datetime.now, index=True)

    class Meta:
        table_name = 'haulage_freight_rates'

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(HaulageFreightRate, self).save(*args, **kwargs)
    
    def set_origin_location_ids(self):
        self.origin_cluster_id = self.origin_location.get('cluster_id')
        self.origin_city_id = self.origin_location.get('city_id')
        self.origin_country_id = self.origin_location.get('country_id')
        self.origin_location_ids = [uuid.UUID(str(self.origin_location_id)), uuid.UUID(str(self.origin_cluster_id)),uuid.UUID(str(self.origin_city_id)),uuid.UUID(str(self.origin_country_id))]

    def set_origin_location_type(self):
        self.origin_location_type = self.origin_location.get('type')

    def set_destination_location_ids(self):
        self.destination_cluster_id = self.destination_location.get('cluster_id')
        self.destination_city_id = self.destination_location.get('city_id')
        self.destination_country_id = self.destination_location.get('country_id')
        self.destination_location_ids = [uuid.UUID(str(self.destination_location_id)), uuid.UUID(str(self.destination_cluster_id)),uuid.UUID(str(self.destination_city_id)),uuid.UUID(str(self.destination_country_id))]

    def validate_container_size(self):
      if self.container_size and self.container_size not in CONTAINER_SIZES:
          raise HTTPException(status_code=400, detail="container size is invalid")

    def validate_container_type(self):
      if self.container_type and self.container_type not in CONTAINER_TYPES:
        raise HTTPException(status_code=400, detail="container type  is invalid")

    def validate_haulage_type(self):
        if self.haulage_type not in HAULAGE_FREIGHT_TYPES:
            raise HTTPException(status_code=400, detail="haulage type is invalid")
    
    def validate_transport_modes(self):
        if not (self.transport_modes.issubset(TRANSPORT_MODES)):
            raise HTTPException(status_code=400, detail="transport modes are invalid")
    
    def validate_transit_time(self):
        if self.transport_modes[0] == 'trailer' and self.transit_time < 0:
            raise HTTPException(status_code=400, detail="transit time is invalid")
    
    def validate_detention_free_time(self):
        if self.transport_modes[0] == 'trailer' and self.detention_free_time < 0:
            raise HTTPException(status_code=400, detail="detention free time is invalid")
    

    def validate_shipping_line_id(self):
        if not self.shipping_line_id:
            return

        shipping_line_data = get_shipping_line(id=self.shipping_line_id)
        if len(shipping_line_data) == 0:
            raise HTTPException(status_code=400, detail="Invalid shipping line ID")

    def validate_service_provider_id(self):
        if not self.service_provider_id:
            return

        service_provider_data = get_organization(id=self.service_provider_id)
        if len(service_provider_data) == 0:
            raise HTTPException(status_code=400, detail="Invalid service provider ID")

    def validate_importer_exporter_id(self):
        if not self.importer_exporter_id:
            return

        importer_exporter_data = get_organization(id=self.importer_exporter_id)
        if len(importer_exporter_data) == 0:
            raise HTTPException(status_code=400, detail="Invalid importer exporter ID")

    def validate_trip_type(self):
        if self.transport_modes[0] == 'trailer' and self.trip_type not in TRIP_TYPES:
            raise HTTPException(status_code=400, detail="Invalid trip type")
    
    def validate_line_items(self, line_items):
      if(not line_items or len(line_items)==0):
        raise HTTPException(status_code=400, detail="line_items required")
    

    def validate_origin_location(self):
        if not self.origin_location_id:
            return

        location_data = maps.list_locations({'filters':{'id':self.origin_location_id}})['list']
        if len(location_data) == 0:
            raise HTTPException(status_code=400, detail="Invalid Origin location ID")


    def validate_destination_location(self):
        if not self.destination_location_id:
            return

        location_data = maps.list_locations({'filters':{'id':self.destination_location_id}})['list']
        if len(location_data) == 0:
            raise HTTPException(status_code=400, detail="Invalid location ID")
        
    def validate_uniqueness(self):
        haulage_cnt = HaulageFreightRate.select().where(
            HaulageFreightRate.origin_location_id == self.origin_location_id,
            HaulageFreightRate.destination_location_id == self.destination_location_id,
            HaulageFreightRate.container_size== self.container_size,
            HaulageFreightRate.container_type == self.container_type,
            HaulageFreightRate.commodity == self.commodity,
            HaulageFreightRate.haulage_type == self.haulage_type,
            HaulageFreightRate.shipping_line_id == self.shipping_line_id,
            HaulageFreightRate.service_provider_id == self.service_provider_id,
            HaulageFreightRate.importer_exporter_id == self.importer_exporter_id,
            HaulageFreightRate.transport_modes_keyword == self.transport_modes_keyword,
            HaulageFreightRate.transit_time == self.transit_time,
            HaulageFreightRate.detention_free_time == self.detention_free_time,
            HaulageFreightRate.trip_type == self.trip_type,
        ).count()

        if haulage_cnt != 0:
            raise HTTPException(status_code=400, detail="Rate already Exists")
        
    def validate_commodity(self):
      if self.container_type and self.commodity in HAULAGE_CONTAINER_TYPE_COMMODITY_MAPPINGS[f"{self.container_type}"]:
        return True
      return False

    def set_destination_location_type(self):
        self.destination_location_type = self.destination_location.get('type')

    def set_origin_destination_location_type(self):
        self.origin_destination_location_type = ':'.join([str(self.origin_location_type),str(self.destination_location_type)])

    def validate_duplicate_line_items(self):
        self.line_items = self.line_items or []
        if len(set(map(lambda t: str(t['code']).upper(), self.line_items))) != len(self.line_items):
            raise HTTPException(status_code=500, detail="Contains Duplicates")
        
    def validate_invalid_line_items(self,possible_charge_codes):
        invalid_line_items = [str(line_item.get('code') or '') for line_item in self.line_items if str(line_item.get('code') or '').strip() not in possible_charge_codes]
        if invalid_line_items:
            raise HTTPException(status_code=500, detail= ','.join(invalid_line_items))
        

    def validate_validity_object(self, validity_start, validity_end):
        if self.transport_modes[0] != 'trailer':
            return
        
        if not validity_start:
            raise HTTPException(status_code=400, detail="validity_start is invalid")
        
        if not validity_end:
            raise HTTPException(status_code=400, detail="validity_end is invalid")

        if validity_end < validity_start:
            raise HTTPException(status_code=400, detail="validity_end can not be lesser than validity_start")
        
    def validate_before_save(self):
        self.validate_container_size()
        self.validate_container_type()
        self.validate_haulage_type()
        self.validate_transport_modes()
        self.validate_transit_time()
        self.validate_detention_free_time()
        self.validate_shipping_line_id()
        self.validate_service_provider_id()
        self.validate_importer_exporter_id()
        self.validate_trip_type()
        self.validate_line_items()
        self.validate_origin_location()
        self.validate_destination_location()
        self.validate_commodity()
        return True
      
    def get_mandatory_line_items(self,mandatory_charge_codes):
        mandatory_line_items = [line_item for line_item in self.line_items if str((line_item.get('code') or '').upper()) in mandatory_charge_codes]
        return mandatory_line_items
    

    def set_platform_price(self,mandatory_charge_codes,currency):
        line_items = self.get_mandatory_line_items(mandatory_charge_codes)

        if not line_items:
            return
        result = self.get_line_items_total_price(line_items)

        rates = HaulageFreightRate.select().where(
            HaulageFreightRate.origin_location_id == self.origin_location_id,
            HaulageFreightRate.destination_location_id == self.destination_location_id,
            HaulageFreightRate.container_size == self.container_size,
            HaulageFreightRate.container_type == self.container_type,
            HaulageFreightRate.commodity == self.commodity,
            HaulageFreightRate.shipping_line_id == self.shipping_line_id,
            HaulageFreightRate.haulage_type == self.haulage_type,
            HaulageFreightRate.transit_time == self.transit_time,
            HaulageFreightRate.detention_free_time == self.detention_free_time,
            HaulageFreightRate.trip_type == self.trip_type,
            HaulageFreightRate.is_line_items_error_messages_present == False,
            HaulageFreightRate.service_provider_id != self.service_provider_id
        ).where(HaulageFreightRate.importer_exporter_id.in_([None, self.importer_exporter_id])).execute()

        sum = 0
        mandatory_line_items = [line_item for line_item in rates.get('line_items') if str((line_item.get('code') or '').upper()) in mandatory_charge_codes]

        for prices in mandatory_line_items:
                sum = sum + int(common.get_money_exchange_for_fcl({'price': prices["price"], 'from_currency': prices['currency'], 'to_currency':currency})['price'])

        if sum and result > sum:
            result = sum

        self.validities['platform_price'] = result

    def get_line_items_total_price(self,line_items):
        currency = line_items[0].currency
        result = 0

        for line_item in line_items:
            result = result + int(common.get_money_exchange_for_fcl({'price': line_item["price"], 'from_currency': line_item['currency'], 'to_currency':currency})['price'])

        return result
    
    def update_platform_prices_for_other_service_providers(self):
        data = {
        "origin_location_id": self.origin_location_id,
        "destination_location_id": self.destination_location_id,
        "container_size": self.container_size,
        "container_type": self.container_type,
        "commodity": self.commodity,
        "transit_time": self.transit_time,
        "detention_free_time": self.detention_free_time,
        "trip_type": self.trip_type,
        # "trailer_type": self.trailer_type,
        "importer_exporter_id": self.importer_exporter_id,
        "shipping_line_id": self.shipping_line_id,
        "haulage_type": self.haulage_type
        }

        update_haulage_rate_platform_prices(data)

    def update_line_item_messages(self,possible_charge_codes):
        self.set_origin_location()
        self.set_destination_location()
        self.set_shipping_line()

        line_items_error_messages = {}
        line_items_info_messages = {}
        is_line_items_error_messages_present = False
        is_line_items_info_messages_present = False

        grouped_charge_codes = {}

        for line_item in self.line_items:
            if grouped_charge_codes.get(line_item.get('code')):
                item = grouped_charge_codes[line_item.get('code')]
            else:
                item = []
            grouped_charge_codes[line_item.get('code')] = item + [line_item]

        for code,line_items in grouped_charge_codes.items():
            code_config = HAULAGE_FREIGHT_CHARGES[code]

            if not code_config:
                line_items_error_messages[code] = ['is invalid']
                is_line_items_error_messages_present = True
                continue

            if len(set(map(lambda item: item.get('unit'), line_items)) - set(code_config['units'])) > 0:
                line_items_error_messages[code] = ["can only be having units " + ", ".join(code_config['units'])]
                is_line_items_error_messages_present = True
                continue

            transport_modes = self.transport_modes
            container_type = self.container_type
            if not eval(str(code_config.get('condition'))):
                line_items_error_messages[code] = ['is invalid']
                is_line_items_error_messages_present = True
                continue
            flag = False
            for slab in line_items:
                if not slab.get('slabs'):
                    flag = True
                    break
            if 'slab_cargo_weight_per_container' in code_config['tags'] and flag:
                line_items_info_messages[code] = ['can contain slab basis rates for higher conversion']
                is_line_items_info_messages_present = True
                continue

        for code, config in possible_charge_codes.items():
            if 'mandatory' in config.get('tags', []):
                if code not in grouped_charge_codes:
                    line_items_error_messages[code] = ['is not present']
                    is_line_items_error_messages_present = True

        for code, config in possible_charge_codes.items():
            if 'additional_service' in config.get('tags', []) or 'shipment_execution_service' in config.get('tags', []):
                if code not in grouped_charge_codes:
                    line_items_info_messages[code] = ['can be added for more conversion']
                    is_line_items_info_messages_present = True

        return {
        'line_items_error_messages': line_items_error_messages,
        'is_line_items_error_messages_present': is_line_items_error_messages_present,
        'line_items_info_messages': line_items_info_messages,
        'is_line_items_info_messages_present': is_line_items_info_messages_present
        }

    def detail(self):
        fcl_customs = {
            'line_items': self.line_items,
            'transit_time': self.transit_time,
            'detention_free_time': self.detention_free_time,
            'trip_type': self.trip_type,
            'validity_start': self.validity_start,
            'validity_end': self.validity_end,
            'trailer_type': self.trailer_type,
            'line_items_info_messages': self.line_items_info_messages,
            'is_line_items_info_messages_present': self.is_line_items_info_messages_present,
            'line_items_error_messages': self.line_items_error_messages,
            'is_line_items_error_messages_present': self.is_line_items_error_messages_present
        }

        return {'fcl_customs': fcl_customs}
    
    def set_origin_location(self):
        if not self.origin_location_id or self.origin_location:
            return
        
        self.origin_location = maps.list_locations({'filters': { 'id': self.origin_location_id}})['list'][0]

    def set_destination_location(self):
        if not self.destination_location_id or self.destination_location:
            return
        
        self.destination_location = maps.list_locations({ 'filters': { 'id': self.destination_location_id}})['list'][0]


    def set_shipping_line(self):
        if not self.shipping_line_id or self.shipping_line:
            return
        
        self.shipping_line = maps.list_operators({ 'filters': { 'id': self.shipping_line_id}})['list'][0]

    def possible_charge_codes(self):
        self.set_origin_location()
        self.set_destination_location()
        self.set_shipping_line()

        haulage_freight_charges_dict = HAULAGE_FREIGHT_CHARGES
        charge_codes = {}
        origin_location = self.origin_location
        destination_location = self.destination_location
        transport_modes = self.transport_modes
        container_type = self.container_type

        for code,config in haulage_freight_charges_dict.items():
            if config.get('condition') is not None and eval(str(config['condition'])):
                if bool(set(self.transport_modes) & set(config['tags'])):
                    charge_codes[code] = config

        return charge_codes

    def mandatory_charge_codes(self,possible_charge_codes):
        charge_codes = {}
        for code,config in possible_charge_codes.items():
            if 'mandatory' in config['tags']:
                charge_codes[code.upper()] = config


        return charge_codes
    

    def delete_rate_not_available_entry(self):

        HaulageFreightRate.delete().where(
            HaulageFreightRate.destination_location_id == self.destination_location_id,
            HaulageFreightRate.origin_location_id == self.origin_location_id,
            HaulageFreightRate.container_size == self.container_size,
            HaulageFreightRate.container_type == self.container_type,
            HaulageFreightRate.commodity == self.commodity,
            HaulageFreightRate.service_provider_id == self.service_provider_id,
            HaulageFreightRate.shipping_line_id == self.shipping_line_id,
            HaulageFreightRate.transport_modes == self.transport_modes,
            HaulageFreightRate.haulage_type == self.haulage_type,
            HaulageFreightRate.transit_time == self.transit_time,
            HaulageFreightRate.detention_free_time == self.detention_free_time,
            HaulageFreightRate.trip_type == self.trip_type,
            HaulageFreightRate.rate_not_available_entry == True
        ).execute()

            



       


        

class FclFreightRateValidity(BaseModel):
    validity_start: datetime.date
    validity_end: datetime.date
    remarks: list[str] = []
    line_items: list[LineItem] = []
    price: float
    platform_price: float = None
    currency: str
    schedule_type: str = None
    payment_term: str = None
    id: str
    likes_count: int = None
    dislikes_count: int = None