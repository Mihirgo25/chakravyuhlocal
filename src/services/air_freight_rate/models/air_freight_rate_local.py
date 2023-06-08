from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
import datetime
from configs.definitions import AIR_FREIGHT_LOCAL_CHARGES
from fastapi import HTTPException
from micro_services.client import *
from celery_worker import get_multiple_service_objects

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class AirFreightRateLocal(BaseModel):
    airline_id = UUIDField(null=True)
    airport_id = UUIDField(null=True)
    bookings_count = IntegerField(null=True)
    bookings_importer_exporters_count = IntegerField(null=True)
    commodity = CharField(null=True)
    commodity_type = CharField(null=True)
    continent_id = UUIDField(null=True)
    country_id = UUIDField(null=True)
    created_at = DateTimeField(null=True)
    currency = CharField(null=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    is_line_items_error_messages_present = BooleanField(null=True)
    is_line_items_info_messages_present = BooleanField(null=True)
    line_items = BinaryJSONField(null=True)
    line_items_error_messages = BinaryJSONField(null=True)
    line_items_info_messages = BinaryJSONField(null=True)
    location_ids = ArrayField(field_class=UUIDField, index=True, null=True)
    min_price = DecimalField(null=True)
    priority_score = IntegerField(null=True)
    priority_score_updated_at = DateTimeField(null=True)
    service_provider_id = UUIDField(null=True)
    spot_searches_count = IntegerField(null=True)
    spot_searches_importer_exporters_count = IntegerField(null=True)
    storage_rate_id = UUIDField(null=True)
    trade_id = UUIDField(null=True)
    trade_type = CharField(null=True)
    updated_at = DateTimeField(null=True)
    rate_type=CharField(null=True)

    class Meta:
        table_name = 'air_freight_rate_locals'
        indexes = (
            (('priority_score', 'id', 'service_provider_id'), False),
            (('priority_score', 'service_provider_id'), False),
            (('updated_at', 'id', 'service_provider_id'), False),
            (('updated_at', 'service_provider_id'), False),
        )
    
    def validate_duplicate_line_items(self):
        line_item_codes = [t.code.upper() for t in self.line_items]
        unique_line_item_codes = set(line_item_codes)

        if len(unique_line_item_codes) != len(line_item_codes):
            self.errors.add('line_items', 'contains duplicates')
    
    def detail(self):
        return {
        'local': {
            'id': self.id,
            'line_items': self.line_items,
            'line_items_info_messages': self.line_items_info_messages,
            'is_line_items_info_messages_present': self.is_line_items_info_messages_present,
            'line_items_error_messages': self.line_items_error_messages,
            'is_line_items_error_messages_present': self.is_line_items_error_messages_present
        }
    }

    def possible_charge_codes(self):
        commodity = self.commodity
        commodity_type = self.commodity_type
        air_freight_local_charges_dict = AIR_FREIGHT_LOCAL_CHARGES
        charge_codes={}
        for code,config in air_freight_local_charges_dict.items():
            if config.get('condition') is not None and eval(str(config['condition'])) and self.trade_type in config['trade_types'] and 'deleted' not in config['tags']:
                charge_codes[code] = config
        return charge_codes
    

    def update_line_item_messages(self):
        line_items_error_messages = {}
        line_items_info_messages = {}
        is_line_items_error_messages_present = False
        is_line_items_info_messages_present = False
         
        air_freight_local_charges_dict = AIR_FREIGHT_LOCAL_CHARGES
        grouped_charge_codes = {}
        for line_item in self.line_items:
            grouped_charge_codes[line_item.get('code')] = line_item

        for code,line_items in grouped_charge_codes.items():
            
            code_config=air_freight_local_charges_dict.get(code)   
            if not code_config:
                
                line_items_error_messages[code] = ['is invalid']
                is_line_items_error_messages_present =True
                continue

            if line_items['unit'] not in code_config['units']:
                
                line_items_error_messages[code] = [f"can only be having units {', '.join(code_config['units'])}"]
                is_line_items_error_messages_present = True
                continue
            
            
            if not eval(str(code_config['condition'])):
                line_items_error_messages[code] = ['is invalid']
                is_line_items_error_messages_present = True
                continue
            
            if 'tags' in code_config and 'weight_slabs_required' in code_config['tags'] and any(not t.get('slabs') for t in line_items):
                
                self.line_items_error_messages[line_items['code']] = ['weight slabs are required']
                self.is_line_items_error_messages_present = True

        possible_charge_codes=self.possible_charge_codes()
        
        for code, config in possible_charge_codes.items():

            if 'mandatory' in config.get('tags', []) and not config.get('locations'):
                if code not in grouped_charge_codes:
                    line_items_error_messages[code] = ['is not present']
                    is_line_items_error_messages_present = True
        
        for code, config in possible_charge_codes.items():
            if 'additional_service' in config['tags'] or 'shipment_execution_service' in config['tags']:
                if grouped_charge_codes.get(code) is None and not line_items_error_messages.get(code):
                    line_items_info_messages[code] = ['can be added for more conversion']
                    is_line_items_info_messages_present = True
        
        self.line_items_error_messages = line_items_error_messages
        self.line_items_info_messages = line_items_info_messages
        self.is_line_items_info_messages_present = is_line_items_info_messages_present
        self.is_line_items_error_messages_present = is_line_items_error_messages_present
        self.save()



    def update_freight_objects(self):
        from services.air_freight_rate.models.air_freight_rate import AirFreightRate

        location_key = 'origin' if self.trade_type == 'export' else 'destination'

        if location_key == 'origin':
            kwargs = {
                'origin_local_id':self.id
            }
        else:
            kwargs = {
                'destination_local_id':self.id
            }
        
        t=AirFreightRate.update(**kwargs).where(
            AirFreightRate.airline_id==self.airline_id,
            AirFreightRate.commodity==self.commodity,
            AirFreightRate.commodity_type==self.commodity_type,
            AirFreightRate.service_provider_id==self.service_provider_id,
            AirFreightRate.rate_type==self.rate_type,
            (eval("AirFreightRate.{}_airport_id".format(location_key)) == self.airport_id),
            (eval("AirFreightRate.{}_local_id".format(location_key)) == None)
        )
        t.execute()
    
    def validate_duplicate_line_items(self):
        item_codes = [item['code'].upper() for item in self.line_items]
        if len(set(item_codes)) != len(item_codes):
            raise HTTPException(status_code=400, detail="Line items contain duplicates")

        
    def validate(self):
        self.validate_duplicate_line_items()
        return True
    
    def set_locations(self):
        ids = []
        if self.airport_id:
           ids.append(str(self.airport_id))

        obj = {'filters':{"id": ids, "type":'airport'}}
        locations_response = maps.list_locations(obj)
        locations = []
        if 'list' in locations_response:
           locations = locations_response["list"]


        for location in locations:
            if str(self.airport_id) == str(location['id']):
               self.airport = self.get_required_location_data(location)
        

    def get_required_location_data(self, location):
        loc_data = {
          "id": location["id"],
          "name": location["name"],
          "airport_code": location["port_code"],
          "country_id": location["country_id"],
          "continent_id": location["continent_id"],
          "trade_id": location["trade_id"],
          "country_code": location["country_code"]
        }
        return loc_data
    
    # def add_service_objects(response):
    #     service_objects=get_multiple_service_objects()
    
    def set_location_ids(self):
        self.country_id = self.airport.get('country_id')
        self.continent_id = self.airport.get('continent_id')
        self.trade_id = self.airport.get('trade_id')
        self.location_ids = [uuid.UUID(str(self.airport_id)),uuid.UUID(str(self.country_id)),uuid.UUID(str(self.trade_id)),uuid.UUID(str(self.continent_id))]







        