import uuid, datetime, json, re
from peewee import DateTimeField, UUIDField, TextField, IntegerField, SQL, BooleanField, FloatField, Model, TextField, CharField
from database.db_session import db
from playhouse.postgres_ext import BinaryJSONField, ArrayField
from fastapi import HTTPException
from micro_services.client  import maps, common
from services.haulage_freight_rate.interactions.update_haulage_freight_rate_platform_prices import update_haulage_freight_rate_platform_prices
from configs.definitions import HAULAGE_FREIGHT_CHARGES
from configs.global_constants import CONTAINER_SIZES, CONTAINER_TYPES
from configs.haulage_freight_rate_constants import HAULAGE_FREIGHT_TYPES, TRANSPORT_MODES, TRIP_TYPES, HAULAGE_CONTAINER_TYPE_COMMODITY_MAPPINGS, TRAILER_TYPES
from configs.haulage_freight_rate_constants import RATE_TYPES
from libs.get_applicable_filters import is_valid_uuid

class UnknownField(object):
    def __init__(self, *_, **__): pass
    
class BaseModel(Model):
    class Meta:
        database = db

class HaulageFreightRate(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    origin_location_id = UUIDField(null=True, index=True)
    origin_cluster_id = UUIDField(null=True, index=True)
    origin_city_id = UUIDField(null=True, index=True)
    destination_location_id = UUIDField(null=True, index=True)
    destination_cluster_id = UUIDField(null=True, index=True)
    destination_city_id = UUIDField(null=True, index=True)
    container_size = TextField(index=True, null=True)
    commodity = TextField(index=True, null=True)
    importer_exporter_id = UUIDField(null=True)
    service_provider_id = UUIDField(null=True, index=True)
    containers_count =  IntegerField(index=True, null=True)
    container_type = TextField(index=True, null=True)
    weight_slabs = BinaryJSONField(index=True, null=True)
    line_items = BinaryJSONField(null=True)
    is_best_price = BooleanField(null=True)
    is_line_items_error_messages_present = BooleanField(index=True, null=True)
    is_line_items_info_messages_present = BooleanField(index=True, null=True)
    line_items_error_messages = BinaryJSONField(index=True, null=True)
    line_items_info_messages = BinaryJSONField(index=True, null=True)
    rate_not_available_entry = BooleanField(constraints=[SQL("DEFAULT false")], null=True, index=True)
    trip_type = TextField(index=True, null=True)
    validity_start = DateTimeField(default=datetime.datetime.now, null=True)
    validity_end = DateTimeField(default = datetime.datetime.now() - datetime.timedelta(30), null=True)
    detention_free_time = IntegerField(index=True, null=True)
    transit_time = IntegerField(index=True, null=True)
    haulage_type = TextField(index=True, null=True, default='merchant')
    transport_modes =ArrayField(TextField, null=True)
    destination_country_id = UUIDField(null=True)
    transport_modes_keyword = TextField(index=True, null=True)
    origin_country_id = UUIDField(null=True, index=True)
    shipping_line_id = UUIDField(null=True, index=True)
    origin_destination_location_type = TextField(index=True, null=True)
    destination_location_type = TextField(index=True, null=True)
    origin_location_type = TextField(index=True, null=True)
    origin_location_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, index=True, null=True)
    destination_location_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, index=True, null=True)
    importer_exporter = BinaryJSONField(null=True)
    service_provider = BinaryJSONField(null=True)
    origin_location = BinaryJSONField(index=True, null=True)
    destination_location = BinaryJSONField(index=True, null=True)
    shipping_line = BinaryJSONField(null=True)
    trailer_type = TextField(index=True, null=True)
    platform_price = FloatField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now, index=True)
    updated_at = DateTimeField(default=datetime.datetime.now, index=True)
    mode = CharField(default = 'manual',index=True, null = True)
    accuracy = FloatField(default = 100, null = True)
    sourced_by_id = UUIDField(null=True, index=True)
    procured_by_id = UUIDField(null=True, index=True)
    sourced_by = BinaryJSONField(null=True)
    procured_by = BinaryJSONField(null=True)
    rate_type = CharField(default='market_place', choices = RATE_TYPES, index=True)
    tags = BinaryJSONField(null=True)
    init_key = TextField(index=True, null=True)

    class Meta:
        table_name = 'haulage_freight_rates_temp'

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(HaulageFreightRate, self).save(*args, **kwargs)
    
    def set_locations(self):
        if not is_valid_uuid(self.origin_location_id):
            raise HTTPException(status_code=400, detail="Invalid origin location")
        if not is_valid_uuid(self.destination_location_id):
            raise HTTPException(status_code=400, detail="Invalid destination location")
        ids = [str(self.origin_location_id), str(self.destination_location_id)]
        locations_response = maps.list_locations({'filters':{"id": ids}, 'includes': {'id': True, 'name': True, 'type': True, 'is_icd': True, 'cluster_id': True, 'city_id': True, 'country_id':True, 'country_code': True}})
        locations = []
        locations = locations_response["list"]
        for location in locations:
            if str(location['id']) == str(self.origin_location_id):
                self.origin_location = self.get_required_location_data(location)
            elif str(location['id']) == str(self.destination_location_id):
                self.destination_location = self.get_required_location_data(location)
        self.set_origin_location_ids()
        self.set_origin_location_type()
        self.set_destination_location_ids()
        self.set_destination_location_type()
        self.set_origin_destination_location_type()

    def get_required_location_data(self, location):
        loc_data = {
          "id": location["id"],
          "name": location["name"],
          "is_icd": location["is_icd"],
          "type": location["type"],
          "cluster_id": location["cluster_id"],
          "city_id": location["city_id"],
          "country_id": location["country_id"],
          "country_code": location["country_code"]
        }
        return loc_data

    def set_origin_location_ids(self):
        self.origin_cluster_id = self.origin_location.get('cluster_id')
        self.origin_city_id = self.origin_location.get('city_id')
        self.origin_country_id = self.origin_location.get('country_id')
        ids = [self.origin_location_id, self.origin_cluster_id, self.origin_city_id, self.origin_country_id]
        self.origin_location_ids = []
        for id in ids:
            if is_valid_uuid(id):
                if type(id) == str:
                    self.origin_location_ids.append(uuid.UUID(id))
                else:
                    self.origin_location_ids.append(id)

    def set_origin_location_type(self):
        self.origin_location_type = self.origin_location.get('type')

    def set_destination_location_ids(self):
        self.destination_cluster_id = self.destination_location.get('cluster_id')
        self.destination_city_id = self.destination_location.get('city_id')
        self.destination_country_id = self.destination_location.get('country_id')
        ids = [self.destination_cluster_id, self.destination_city_id, self.destination_country_id, self.destination_location_id]
        self.destination_location_ids = []
        for id in ids:
            if is_valid_uuid(id):
                if type(id) == str:
                    self.destination_location_ids.append(uuid.UUID(id))
                else:
                    self.destination_location_ids.append(id)
    
    def set_destination_location_type(self):
        self.destination_location_type = self.destination_location.get('type')
    
    def set_origin_destination_location_type(self):
        self.origin_destination_location_type = ':'.join([str(self.origin_location_type),str(self.destination_location_type)])
    
    def validate_validity_object(self, validity_start, validity_end):
        if not self.transport_modes:
            raise HTTPException(status_code=400, detail="transport mode can't be empty")

        if self.transport_modes[0] != 'trailer' :
            return
        
        if not validity_start:
            raise HTTPException(status_code=400, detail="validity_start is invalid")
        
        if not validity_end:
            raise HTTPException(status_code=400, detail="validity_end is invalid")

        if validity_end < validity_start:
            raise HTTPException(status_code=400, detail="validity_end can not be lesser than validity_start")
    
    def validate_container_size(self):
      if self.container_size and self.container_size not in CONTAINER_SIZES:
          raise HTTPException(status_code=400, detail="container size is invalid")
    
    def validate_container_type(self):
      if self.container_type and self.container_type not in CONTAINER_TYPES:
        raise HTTPException(status_code=400, detail="container type  is invalid")
    
    def validate_haulage_type(self):
        if self.haulage_type not in HAULAGE_FREIGHT_TYPES:
            raise HTTPException(status_code=400, detail="haulage type is invalid")
        
    def validate_trailer_type(self):
        if self.transport_modes[0] == 'trailer' and self.trailer_type not in TRAILER_TYPES:
            raise HTTPException(status_code=400, detail="trailer type is invalid")
    
    def validate_transport_modes(self):
        if not all(element in TRANSPORT_MODES for element in self.transport_modes):
            raise HTTPException(status_code=400, detail="transport modes are invalid")
    
    def validate_transit_time(self):
        if self.transit_time is not None:
            if self.transport_modes[0] == 'trailer' and self.transit_time < 0:
                raise HTTPException(status_code=400, detail="transit time is invalid")
    
    def validate_detention_free_time(self):
        if self.detention_free_time is not None:
            if self.transport_modes[0] == 'trailer' and self.detention_free_time < 0:
                raise HTTPException(status_code=400, detail="detention free time is invalid")

    def validate_shipping_line_id(self):
        if not self.shipping_line_id and self.haulage_type == 'carrier':
            raise HTTPException(status_code=400, detail="shipping line id is required for carrier")

    def validate_trip_type(self):
        if self.transport_modes[0] == 'trailer' and self.trip_type and  self.trip_type not in TRIP_TYPES:
            raise HTTPException(status_code=400, detail="Invalid trip type")
    
    def validate_line_items(self):
      if not self.line_items:
        raise HTTPException(status_code=400, detail="line_items required")
        
    def validate_commodity(self):
      if self.container_type and self.commodity in HAULAGE_CONTAINER_TYPE_COMMODITY_MAPPINGS[f"{self.container_type}"]:
        return True
      else:
        raise HTTPException(status_code=400, detail="Invalid commodity")

    def validate_duplicate_line_items(self):
        self.line_items = self.line_items or []
        if len(set(map(lambda t: str(t['code']).upper(), self.line_items))) != len(self.line_items):
            raise HTTPException(status_code=500, detail="Contains Duplicates")
        
   
    def validate_invalid_line_items(self):
        haulage_line_item_codes = [str(t['code']) for t in self.line_items]
        possible_haulage_charge_codes = [str(key) for key in self.possible_charge_codes().keys()]
        invalid_haulage_line_items = [t for t in haulage_line_item_codes if t not in possible_haulage_charge_codes]
        if invalid_haulage_line_items:
            raise HTTPException(status_code=400, detail="Invalid line items")
        
    def validate_before_save(self):
        self.validate_container_size()
        self.validate_container_type()
        self.validate_haulage_type()
        self.validate_trailer_type()
        self.validate_transport_modes()
        self.validate_transit_time()
        self.validate_detention_free_time()
        self.validate_shipping_line_id()
        self.validate_trip_type()
        self.validate_line_items()
        self.validate_commodity()
        self.validate_duplicate_line_items()
        self.validate_invalid_line_items()
        self.validate_slabs()
        return True
        
      
    def get_mandatory_line_items(self,mandatory_charge_codes):
        mandatory_line_items = [line_item for line_item in self.line_items if str((line_item.get('code') or '').upper()) in mandatory_charge_codes]
        return mandatory_line_items
    

    def set_platform_price(self):
        possible_charge_codes = self.possible_charge_codes()
        mandatory_charge_codes = self.mandatory_charge_codes(possible_charge_codes)
        line_items = self.get_mandatory_line_items(mandatory_charge_codes)
        if not line_items:
            return
        currency=self.line_items[0].get('currency')
        result = self.get_line_items_total_price(line_items)

        rates = HaulageFreightRate.select().where(
            HaulageFreightRate.origin_location_id == self.origin_location_id,
            HaulageFreightRate.destination_location_id == self.destination_location_id,
            HaulageFreightRate.container_size == self.container_size,
            HaulageFreightRate.container_type == self.container_type,
            HaulageFreightRate.commodity == self.commodity,
            HaulageFreightRate.shipping_line_id == self.shipping_line_id,
            HaulageFreightRate.haulage_type == self.haulage_type,
            HaulageFreightRate.trailer_type == self.trailer_type,
            HaulageFreightRate.transit_time == self.transit_time,
            HaulageFreightRate.detention_free_time == self.detention_free_time,
            HaulageFreightRate.trip_type == self.trip_type,
            HaulageFreightRate.is_line_items_error_messages_present == False,
            HaulageFreightRate.service_provider_id != self.service_provider_id
        ).where(HaulageFreightRate.importer_exporter_id.in_([None, self.importer_exporter_id])).execute()
        
        rates = list(rates)
        sum = 0
        if rates:
            mandatory_line_items = [line_item for line_item in rates.get('line_items') if str((line_item.get('code') or '').upper()) in mandatory_charge_codes]

            for prices in mandatory_line_items:
                    sum = sum + int(common.get_money_exchange_for_fcl({'price': prices["price"], 'from_currency': prices['currency'], 'to_currency':currency})['price'])

            if sum and result > sum:
                result = sum

            self.platform_price = result

    def set_is_best_price(self):
        if not self.platform_price:
            return
        
        possible_charge_codes = self.possible_charge_codes()
        mandatory_charge_codes = self.mandatory_charge_codes(possible_charge_codes)
        line_items = self.get_mandatory_line_items(mandatory_charge_codes)

        total_price = self.get_line_items_total_price(line_items)

        self.is_best_price = (total_price <= self.platform_price)


    def get_line_items_total_price(self,line_items):
        currency = line_items[0].get('currency')
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
        "trailer_type": self.trailer_type,
        "importer_exporter_id": self.importer_exporter_id,
        "shipping_line_id": self.shipping_line_id,
        "haulage_type": self.haulage_type
        }

        update_haulage_freight_rate_platform_prices(data)

    def update_line_item_messages(self,possible_charge_codes):

        self.line_items_error_messages = {}
        self.line_items_info_messages = {}
        self.is_line_items_error_messages_present = False
        self.is_line_items_info_messages_present = False

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
                self.line_items_error_messages[code] = ['is invalid']
                self.is_line_items_error_messages_present = True
                continue

            if len(set(map(lambda item: item.get('unit'), line_items)) - set(code_config['units'])) > 0:
                self.line_items_error_messages[code] = ["can only be having units " + ", ".join(code_config['units'])]
                self.is_line_items_error_messages_present = True
                continue

            transport_modes = self.transport_modes
            container_type = self.container_type
            origin_location = self.origin_location
            destination_location = self.destination_location
            if not eval(str(code_config.get('condition'))):
                self.line_items_error_messages[code] = ['is invalid']
                self.is_line_items_error_messages_present = True
                continue
            flag = False
            for slab in line_items:
                if not slab.get('slabs'):
                    flag = True
                    break
            if 'slab_cargo_weight_per_container' in code_config['tags'] and flag:
                self.line_items_info_messages[code] = ['can contain slab basis rates for higher conversion']
                self.is_line_items_info_messages_present = True
                continue

        for code, config in possible_charge_codes.items():
            if 'mandatory' in config.get('tags', []):
                if code not in grouped_charge_codes:
                    self.line_items_error_messages[code] = ['is not present']
                    self.is_line_items_error_messages_present = True

        for code, config in possible_charge_codes.items():
            if 'additional_service' in config.get('tags', []) or 'shipment_execution_service' in config.get('tags', []):
                if code not in grouped_charge_codes:
                    self.line_items_info_messages[code] = ['can be added for more conversion']
                    self.is_line_items_info_messages_present = True

        return {
        'line_items_error_messages': self.line_items_error_messages,
        'is_line_items_error_messages_present': self.is_line_items_error_messages_present,
        'line_items_info_messages': self.line_items_info_messages,
        'is_line_items_info_messages_present': self.is_line_items_info_messages_present
        }

    def detail(self):
        haulage_freight = {
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

        return {'haulage_freight': haulage_freight}

    def possible_charge_codes(self):
        haulage_freight_charges_dict = HAULAGE_FREIGHT_CHARGES

        charge_codes = {}
        origin_location = self.origin_location
        destination_location = self.destination_location
        transport_modes = self.transport_modes
        container_type = self.container_type
        if not isinstance(self.transport_modes, list):
            self.transport_modes = json.loads(self.transport_modes[0])
        else:
            self.transport_modes = self.transport_modes
        for code,config in haulage_freight_charges_dict.items():
            if eval(str(config['condition'])) and bool(set(self.transport_modes) & set(config['tags'])):
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
            HaulageFreightRate.trailer_type == self.trailer_type,
            HaulageFreightRate.rate_not_available_entry == True
        ).execute()

    def validate_slabs(self):
        # check once
        slabs = self.line_items[0].get('slabs') or []
        for index, slab in enumerate(slabs):
            if (float(slab['upper_limit']) <= float(slab['lower_limit'])) or (index!=0 and float(slab['lower_limit'])<= float(slabs[index-1]['upper_limit'])):
                raise HTTPException(status_code=400, detail=f"{slabs} are not valid {slab['code']} in line item")

