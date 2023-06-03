from peewee import *
import datetime
from database.db_session import db
from fastapi import HTTPException
from configs.air_freight_rate_constants import MAX_CARGO_LIMIT
from playhouse.postgres_ext import *
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from configs.definitions import AIR_FREIGHT_WAREHOUSE_CHARGES
from configs.air_freight_rate_constants import LOCAL_COMMODITIES
from micro_services.client import *
from database.rails_db import get_organization,get_shipping_line

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class AirFreightWarehouseRates(BaseModel):
    airport_id = UUIDField(null=True)
    bookings_count = IntegerField(null=True)
    bookings_importer_exporters_count = IntegerField(null=True)
    commodity = CharField(null=True)
    continent_id = UUIDField(null=True)
    country_id = UUIDField(null=True)
    created_at = DateTimeField()
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    importer_exporter_id = UUIDField(null=True)
    is_line_items_error_messages_present = BooleanField(null=True)
    is_line_items_info_messages_present = BooleanField(null=True)
    line_items = BinaryJSONField(null=True)
    line_items_error_messages = BinaryJSONField(null=True)
    line_items_info_messages = BinaryJSONField(null=True)
    location_ids = ArrayField(field_class=UUIDField, index=True, null=True)
    priority_score = IntegerField(null=True)
    priority_score_updated_at = DateTimeField(null=True)
    rate_not_available_entry = BooleanField(constraints=[SQL("DEFAULT false")], null=True)
    service_provider_id = UUIDField(null=True)
    spot_searches_count = IntegerField(null=True)
    spot_searches_importer_exporters_count = IntegerField(null=True)
    trade_id = UUIDField(null=True)
    trade_type = CharField(null=True)
    updated_at = DateTimeField()
    performed_by_id=CharField(null=True)
    procured_by_id=CharField(null=True)
    sourced_by_id=CharField(null=True)

    class Meta:
        table_name = 'air_freight_warehouse_rates'

    def detail(self):

        return  { 
            'warehouse':{
                'id':self.id,
                # 'is_best_price':self.is_best_price #is_best_price not present in table
                'line_items':self.line_items,
                'line_items_info_messages':self.line_items_info_messages,
                'is_line_items_info_messages_present':self.is_line_items_info_messages_present,
                'line_items_error_messages':self.line_items_error_messages,
                'is_line_items_error_messages_present':self.is_line_items_error_messages_present
            }
        }
        
    def validate_trade_type(self):
        if self.trade_type not in ['import', 'export', 'domestic']:
            raise HTTPException(status_code=500,detail='invalid trade_type')
    
    def validate_commodity(self):
        if self.commodity not in LOCAL_COMMODITIES:
            raise HTTPException(status_code=400,detail='invalid commodity')

    def validate_service_provider_id(self):
        service_provider_data = get_organization(id=self.service_provider_id)
        if len(service_provider_data) == 0:
            raise HTTPException(status_code=400, detail="Invalid service provider ID")
    
    def validate_airport_id(self):
        obj = {"filters":{"id": [(str(self.airport_id))],'type':'airport'}}
        airport = maps.list_locations(obj)['list']
        if airport:
            airport =airport[0]
            self.airport = {key:value for key,value in airport.items() if key in ['id', 'name','display_name']}
            self.country_id = airport.get('country_id', None)
            self.trade_id = airport.get('trade_id', None)
            self.continent_id = airport.get('continent_id', None)
            self.location_ids = [uuid.UUID(str(x)) for x in [self.airport_id, self.country_id, self.trade_id] if x is not None]
        else:
            raise HTTPException(status_code=500,detail='Invalid airport')


    def validate(self):
        self.validate_trade_type()
        self.validate_commodity()
        self.validate_service_provider_id()
        self.validate_airport_id()
        
        return True

    def update_freight_object(self):
        location_key = 'origin' if self.trade_type == 'export' else 'destination'

        freight_query=AirFreightRate.update(warehouse_rate_id=self.id).where(AirFreightRate.commodity==self.commodity,
                                                    AirFreightRate.service_provider_id==self.service_provider_id).where(
                                                    AirFreightRate.warehouse_rate_id.is_null()).where(
                                                    getattr(AirFreightRate,f'{location_key}_airport_id')==self.airport_id).execute()
    
    def possible_charge_codes(self):
        commodity = self.commodity
        air_freight_local_charges_dict =AIR_FREIGHT_WAREHOUSE_CHARGES
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
         
        air_freight_local_charges_dict = AIR_FREIGHT_WAREHOUSE_CHARGES
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

    def delete_rate_not_available_entry(self):
        AirFreightWarehouseRates.delete().where(
            AirFreightWarehouseRates.airport_id==self.airport_id,
            AirFreightWarehouseRates.trade_type==self.trade_type,
            AirFreightWarehouseRates.commodity==self.commodity,
            AirFreightWarehouseRates.service_provider_id==self.service_provider_id,
            AirFreightWarehouseRates.rate_not_available_entry==True
        ).execute()
            