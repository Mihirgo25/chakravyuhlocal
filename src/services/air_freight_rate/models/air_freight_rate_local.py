from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
import datetime
from configs.definitions import AIR_FREIGHT_LOCAL_CHARGES
from fastapi import HTTPException
from micro_services.client import *
from database.rails_db import *
from services.air_freight_rate.constants.air_freight_rate_constants import *
from configs.global_constants import *
class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class AirFreightRateLocal(BaseModel):
    airline = BinaryJSONField(null=True)
    airline_id = UUIDField(null=True,index=True)
    airport = BinaryJSONField(null=True)
    airport_id = UUIDField(null=True,index=True)
    # bookings_count = IntegerField(null=True)
    # bookings_importer_exporters_count = IntegerField(null=True)
    commodity = CharField(null=True)
    commodity_type = CharField(null=True)
    continent_id = UUIDField(null=True)
    country_id = UUIDField(null=True)
    created_at = DateTimeField(null=True,default=datetime.datetime.now())
    # currency = CharField(null=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    is_line_items_error_messages_present = BooleanField(null=True)
    is_line_items_info_messages_present = BooleanField(null=True)
    line_items = BinaryJSONField(null=True)
    line_items_error_messages = BinaryJSONField(null=True)
    line_items_info_messages = BinaryJSONField(null=True)
    location_ids = ArrayField(field_class=UUIDField, index=True, null=True)
    # min_price = FloatField(null=True)
    # priority_score = IntegerField(null=True)
    # priority_score_updated_at = DateTimeField(null=True)
    service_provider = BinaryJSONField(null=True)
    service_provider_id = UUIDField(null=True,index=True)
    # spot_searches_count = IntegerField(null=True)
    # spot_searches_importer_exporters_count = IntegerField(null=True)
    storage_rate_id = UUIDField(null=True)
    trade_id = UUIDField(null=True)
    trade_type = CharField(null=True)
    updated_at = DateTimeField(null=True,index=True,default=datetime.datetime.now())
    sourced_by_id = UUIDField(null=True, index=True)
    procured_by_id = UUIDField(null=True, index=True)
    sourced_by = BinaryJSONField(null=True)
    procured_by = BinaryJSONField(null=True)
    rate_type=CharField(null=True)
    is_active=BooleanField(null=True,default=True)

    class Meta:
        table_name = 'air_freight_rate_locals'

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(AirFreightRateLocal, self).save(*args, **kwargs)
    
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
        commodity_sub_type = None
        

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

            if self.trade_type not in  code_config['trade_types']:
                line_items_error_messages[code] = ["can only be added for {}".format(",".join(code_config['trade_types']))]

            if line_items['unit'] not in code_config['units']:
                line_items_error_messages[code] = [f"can only be having units {', '.join(code_config['units'])}"]
                is_line_items_error_messages_present = True
                continue
            
            
            if not eval(str(code_config['condition'])):
                line_items_error_messages[code] = ['is invalid']
                is_line_items_error_messages_present = True
                continue
            
            if code_config['tags'] and 'weight_slabs_required' in code_config['tags'] and not line_items.get('slabs'):
                self.line_items_error_messages[code] = ['weight slabs are required']
                self.is_line_items_error_messages_present = True

        possible_charge_codes=self.possible_charge_codes()
        
        for code, config in possible_charge_codes.items():
            if 'mandatory' in config.get('tags', []):
                if code not in grouped_charge_codes:
                    line_items_error_messages[code] = ['is not present']
                    is_line_items_error_messages_present = True

            if 'additional_service' in config['tags']:
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
        line_items = {}
        for line_item in self.line_items:
            if line_item['code'] in line_items.keys():
                raise HTTPException(status_code = 400, details = 'Duplicate Line Items')
            line_items[line_item['code']] = True

    
    def validate_commodity(self):
        if self.commodity not in COMMODITY:
            raise HTTPException(status_code=400,details = 'Invalid Commodity')

    def validate_commodity_type(self):
        if self.commodity_type not in COMMODITY_TYPE:
            raise HTTPException(status_code=400,details = 'Invalid Commodity Type')

    def validate_service_provider_id(self):
        service_provider_data = get_organization(id=str(self.service_provider_id))
        if (len(service_provider_data) != 0) and service_provider_data[0].get('account_type') == 'service_provider':
            self.service_provider = service_provider_data[0]
            return True
        raise HTTPException(status_code = 400, details = 'Service Provider Id Is Not Valid') 
    
    def validate(self):
        if not self.airport:
            raise HTTPException(status_code = 400, detail = 'Airport is Invalid')
        
        if not self.airline:
             raise HTTPException(status_code = 400, detail = 'Airline is Invalid')         
        self.validate_duplicate_line_items()
        self.validate_commodity()
        self.validate_commodity_type()
        self.validate_service_provider_id()
        
        if self.trade_type not in TRADE_TYPES:
            raise HTTPException(staus_code = 400, detail = 'Invalid Trade Type')
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
    
    def set_airline(self):
        if self.airline or not self.airline_id:
            return
        airline = get_shipping_line(id=self.airline_id,operator_type='airline')
        if len(airline) != 0:
            self.airline = {key:str(value) for key,value in airline[0].items() if key in ['id', 'business_name', 'short_name', 'logo_url']}

    def get_required_location_data(self, location):
        loc_data = {
          "id": location["id"],
          "name": location["name"],
          "display_name":location['display_name'],
          "port_code": location["port_code"],
          "country_id": location["country_id"],
          "continent_id": location["continent_id"],
          "trade_id": location["trade_id"],
          "country_code": location["country_code"]
        }
        return loc_data
    
    
    def set_location_ids(self):
        self.country_id = self.airport.get('country_id')
        self.continent_id = self.airport.get('continent_id')
        self.trade_id = self.airport.get('trade_id')
        self.location_ids = [uuid.UUID(str(self.airport_id)),uuid.UUID(str(self.country_id)),uuid.UUID(str(self.trade_id)),uuid.UUID(str(self.continent_id))]

    def update_foreign_references(self):
        return





        