from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
import datetime
from services.air_freight_rate.air_freight_rate_params import LineItem
from fastapi import HTTPException
from configs.definitions import AIR_FREIGHT_SURCHARGES
from micro_services.client import maps
from services.air_freight_rate.constants.air_freight_rate_constants import *
from database.rails_db import get_organization,get_operators

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class AirFreightRateSurcharge(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    origin_airport_id=UUIDField(index=True,null=True)
    origin_country_id=UUIDField(null=True,index=True)
    origin_trade_id=UUIDField(null=True,index=True)
    origin_continent_id=UUIDField(null=True,index=True)
    destination_airport_id=UUIDField(index=True,null=True)
    destination_country_id=UUIDField(null=True,index=True)
    destination_trade_id=UUIDField(null=True,index=True)
    destination_continent_id=UUIDField(null=True,index=True)
    commodity=CharField(null=True,index=True)
    commodity_type=CharField(null=True,index=True)
    origin_airport=BinaryJSONField(null=True)
    destination_airport=BinaryJSONField(null=True)
    airline_id=UUIDField(null=True,index=True)
    service_provider_id=UUIDField(null=True,index=True)
    is_line_items_error_messages_present = BooleanField(null=True)
    is_line_items_info_messages_present = BooleanField(null=True)
    line_items = BinaryJSONField(null=True)
    line_items_error_messages = BinaryJSONField(null=True)
    line_items_info_messages = BinaryJSONField(null=True)
    airline=BinaryJSONField(null=True)
    service_provider=BinaryJSONField(null=True)
    origin_location_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, index=True, null=True)
    destination_location_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, index=True, null=True)
    operation_type=CharField(null=True)
    sourced_by_id=UUIDField(null=True,index=True)
    procured_by_id=UUIDField(null=True,index=True)
    sourced_by = BinaryJSONField(null=True)
    procured_by = BinaryJSONField(null=True)
    is_active=BooleanField(null=True)
    updated_at=DateTimeField(default=datetime.datetime.now,index=True)
    created_at=DateTimeField(default=datetime.datetime.now,index=True)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(AirFreightRateSurcharge, self).save(*args, **kwargs)
    
    class Meta:
        table_name = 'air_freight_rate_surcharges'

    def detail(self):
        return {
        'surcharge': {
            'id': self.id,
            'line_items': self.line_items,
            'line_items_info_messages': self.line_items_info_messages,
            'is_line_items_info_messages_present': self.is_line_items_info_messages_present,
            'line_items_error_messages': self.line_items_error_messages,
            'is_line_items_error_messages_present': self.is_line_items_error_messages_present
        }
    }

    def update_line_item_messages(self):
        line_items_error_messages = {}
        line_items_info_messages = {}
        is_line_items_error_messages_present = False
        is_line_items_info_messages_present = False


        air_freight_surcharges_dict = AIR_FREIGHT_SURCHARGES
        grouped_charge_codes = {}
        for line_item in self.line_items:
            grouped_charge_codes[line_item.get('code')] = line_item
      

        for code, line_items in grouped_charge_codes.items():
            code_config = air_freight_surcharges_dict.get(code)
            if not code_config:
                line_items_error_messages[code] = ['is invalid']
                is_line_items_error_messages_present = True
                continue

            if line_items['unit'] not in code_config['units']:
                line_items_error_messages[code] = [f"can only be having units {', '.join(code_config['units'])}"]
                is_line_items_error_messages_present = True
                continue

            if not eval(str(code_config['condition'])):
                line_items_error_messages[code] = ['is invalid']
                is_line_items_error_messages_present = True
                continue
        
        
        possible_charge_codes=self.possible_charge_codes()
        for code, config in possible_charge_codes.items():
    
            if 'mandatory' in config.get('tags', []):
                if code not in grouped_charge_codes:
                    line_items_error_messages[code] = ['is not present']
                    is_line_items_error_messages_present = True
       
            if 'additional_service' in config['tags'] or 'shipment_execution_service' in config['tags']:
                if not grouped_charge_codes.get(code):
                    line_items_info_messages[code] = ['can be added for more conversion']
                    is_line_items_info_messages_present = True

        self.line_items_error_messages = line_items_error_messages
        self.line_items_info_messages = line_items_info_messages
        self.is_line_items_info_messages_present = is_line_items_info_messages_present
        self.is_line_items_error_messages_present = is_line_items_error_messages_present
        
    def update_freight_objects(self):
        from services.air_freight_rate.models.air_freight_rate import AirFreightRate
        surcharge = {
            'line_items':self.line_items,
            'line_items_info_messages': self.line_items_info_messages,
            'is_line_items_info_messages_present': self.is_line_items_info_messages_present,
            'line_items_error_messages': self.line_items_error_messages,
            'is_line_items_error_messages_present': self.is_line_items_error_messages_present
        }
        try:
            t = AirFreightRate.update(surcharge_id=self.id,surcharge = surcharge).where(
                (AirFreightRate.origin_airport_id == self.origin_airport_id),
                (AirFreightRate.destination_airport_id == self.destination_airport_id),
                (AirFreightRate.commodity == self.commodity) ,
                (AirFreightRate.commodity_type == self.commodity_type) ,
                (AirFreightRate.operation_type == self.operation_type) ,
                (AirFreightRate.airline_id == self.airline_id) ,
                (AirFreightRate.service_provider_id == self.service_provider_id),
                (AirFreightRate.surcharge_id.is_null(True)),
                (AirFreightRate.price_type == "net_net")).execute()
        except Exception as e:
            print(e)
    
    def set_origin_location_ids(self):
        self.origin_country_id = self.origin_airport.get('country_id')
        self.origin_continent_id = self.origin_airport.get('continent_id')
        self.origin_trade_id = self.origin_airport.get('trade_id')
        self.origin_location_ids = [uuid.UUID(str(self.origin_airport_id)),uuid.UUID(str(self.origin_country_id)),uuid.UUID(str(self.origin_trade_id)),uuid.UUID(str(self.origin_continent_id))]

    def set_destination_location_ids(self):
        self.destination_country_id = self.destination_airport.get('country_id')
        self.destination_continent_id = self.destination_airport.get('continent_id')
        self.destination_trade_id = self.destination_airport.get('trade_id')
        self.destination_location_ids = [uuid.UUID(str(self.destination_airport_id)),uuid.UUID(str(self.destination_country_id)),uuid.UUID(str(self.destination_trade_id)),uuid.UUID(str(self.destination_continent_id))] 
    
    def validate_origin_destination_country(self):
        if self.origin_airport['country_code'] == self.destination_airport['country_code']:
            raise HTTPException(status_code=400, detail="Destination airport can not be in the same country as origin_airport")
    
    def validate_duplicate_line_items(self):
        line_items = {}
        for line_item in self.line_items:
            if line_item['code'] in line_items.keys():
                raise HTTPException(status_code = 400, details = 'Duplicate Line Items')
            line_items[line_item['code']] = True
        
    def possible_charge_codes(self):
        commodity = self.commodity
        commodity_type = self.commodity_type
        air_freight_surcharges = AIR_FREIGHT_SURCHARGES


        charge_codes = {}
    
        for k,v in air_freight_surcharges.items():
            if eval(str(v['condition'])):
                charge_codes[k] = v
        return charge_codes
    
    def validate_service_provider_id(self):
        service_provider_data = get_organization(id=str(self.service_provider_id))
        if (len(service_provider_data) != 0) and service_provider_data[0].get('account_type') == 'service_provider':
            self.service_provider = service_provider_data[0]
            return True
        raise HTTPException(status_code = 400, details = 'Service Provider Id Is Not Valid') 
    
    def validate_airline_id(self):
        airline_data = get_operators(id=self.airline_id,operator_type='airline')
        if (len(airline_data) != 0) and airline_data[0].get('operator_type') == 'airline':
            self.airline = airline_data[0]
            return True
        raise HTTPException(status_code = 400, details = 'Airline Id Is Not Valid')    
    
    def validate(self):
        if self.operation_type not in AIR_OPERATION_TYPES:
            raise HTTPException(status_code = 400, detail = 'Invalid Operation Type')
        self.validate_duplicate_line_items()
        self.validate_origin_destination_country()
        self.validate_service_provider_id()
        self.validate_airline_id()
        if not self.origin_airport:
            raise HTTPException(status_code = 400, detail = 'Invalid Origin Airport')
        
        if not self.destination_airport:
            raise HTTPException(status_code = 400, detail = 'Invalid Destination Airport')
        
        if self.commodity not in COMMODITY:
            raise HTTPException(status_code = 400, detail = 'Invalid Commodity')
        
        if self.commodity_type not in COMMODITY_TYPE:
            raise HTTPException(status_code = 400, detail = 'Invalid Commodity Type')
        return True
    
    def set_locations(self):
        ids = [str(self.origin_airport_id), str(self.destination_airport_id)]
        if self.origin_airport_id:
           ids.append(str(self.origin_airport_id))
        if self.destination_airport_id:
           ids.append(str(self.destination_airport_id))

        obj = {'filters':{"id": ids, "type":'airport'}}
        locations_response = maps.list_locations(obj)
        locations = []
        if 'list' in locations_response:
           locations = locations_response["list"]

        for location in locations:
            if str(self.origin_airport_id) == str(location['id']):
               self.origin_airport = self.get_required_location_data(location)
            if str(self.destination_airport_id) == str(location['id']):
               self.destination_airport = self.get_required_location_data(location)

    def get_required_location_data(self, location):
        loc_data = {
            "id": location["id"],
          "type":location['type'],
          "name":location['name'],
          "display_name": location["display_name"],
          "is_icd": location["is_icd"],
          "port_code": location["port_code"],
          "country_id": location["country_id"],
          "continent_id": location["continent_id"],
          "trade_id": location["trade_id"],
          "country_code": location["country_code"]
        }
        return loc_data