from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
import datetime
from configs.definitions import AIR_FREIGHT_LOCAL_CHARGES
from services.air_freight_rate.models.air_freight_rate import AirFreightRate


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
    created_at = DateTimeField()
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
    updated_at = DateTimeField()
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

    def possible_charge_codes(self):
        air_freight_local_charges_dict = AIR_FREIGHT_LOCAL_CHARGES
        charge_codes={}
        for code,config in air_freight_local_charges_dict.items():
            if config.get('condition') is not None and eval(str(config['condition'])) and self.trade_type in config['trade_types'] and 'deleted' not in config['tags']:
                charge_codes[code] = config

    def update_line_item_messages(self):
        
        self.line_items_error_messages = {}
        self.line_items_info_messages = {}
        self.is_line_items_error_messages_present = False
        self.is_line_items_info_messages_present = False
        grouped_charge_codes = {}
        
        
        for line_item in self.line_items:
            if line_item['code'] not in grouped_charge_codes:
                grouped_charge_codes['line_items'] = []
            grouped_charge_codes['line_items'].append(line_item)

        for line_items in grouped_charge_codes['line_items']:
            code_config=AIR_FREIGHT_LOCAL_CHARGES   
            if not code_config:
                self.line_items_error_messages[line_items['code']] = ['is invalid']
                self.is_line_items_error_messages_present =True
            
            # if self.trade_type not in code_config['code']['trade_types']:     
                   
            #     self.line_items_error_messages[code] = ["can only be added for {}".format(", ".join(code_config['trade_types']))]
            #     self.is_line_items_error_messages_present = True

            if len(set(line_items['unit'])  - set(code_config[line_items['code']]["units"])) > 0:
                self.line_items_error_messages[code] = ["can only be having units {}".format(", ".join(code_config["units"]))]
                
                self.is_line_items_error_messages_present = True
                continue
            
            
            # if not eval(str(code_config['condition'])):
            #     print(12345678)
            #     self.line_items_error_messages[line_items['code']] = ['is invalid']
            #     self.is_line_items_error_messages_present = True

            if 'tags' in code_config and 'weight_slabs_required' in code_config['tags'] and any(not t.get('slabs') for t in line_items):
                
                self.line_items_error_messages[line_items['code']] = ['weight slabs are required']
                self.is_line_items_error_messages_present = True

            for code, config in possible_charge_codes.items():
                if 'mandatory' in config.get('tags', []):
                    if not grouped_charge_codes[code]:
                        self.line_items_error_messages[code] = ['is not present']
                        self.is_line_items_error_messages_present = True

            for code, config in possible_charge_codes.items(): 
                if 'additional_service' in config.get('tags', []):
                    if not grouped_charge_codes[code]:
                        self.line_items_info_messages[code] = ['can be added for more conversion']
                        self.is_line_items_info_messages_present = True
            


    def update_freight_objects(self):
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
            (eval("FclFreightRate.{}_airport_id".format(location_key)) == self.airport_id),
            (eval("FclFreightRate.{}_local_id".format(location_key)) == None)
        )
        t.execute()


        