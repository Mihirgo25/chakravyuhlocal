from peewee import * 
import datetime
from database.db_session import db
from playhouse.postgres_ext import *
from services.air_freight_rate.constants.air_freight_rate_constants import LOCAL_COMMODITIES
from fastapi import HTTPException
from configs.global_constants import TRADE_TYPES
from services.air_freight_rate.models.air_freight_rate_local import AirFreightRateLocal
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from micro_services.client import *
from database.rails_db import *

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True
class AirFreightStorageRates(BaseModel):
    airline_id = UUIDField(null=True,index=True)
    airline=BinaryJSONField(null=True)
    airport_id = UUIDField(null=True,index=True)
    airport=BinaryJSONField(null=True)
    commodity = CharField(null=True,index=True)
    continent_id = UUIDField(null=True)
    country_id = UUIDField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now())
    free_limit = IntegerField(null=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    # importer_exporter_id = UUIDField(null=True,index= True) check whether to keep this colu,mn or not 
    is_slabs_missing = BooleanField(null=True)
    location_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, index=True, null=True)
    priority_score = IntegerField(null=True)
    priority_score_updated_at = DateTimeField(null=True)
    remarks = ArrayField(constraints=[SQL("DEFAULT '{}'::character varying[]")], field_class=CharField, null=True)
    service_provider_id = UUIDField(null=True,index=True)
    service_provider=BinaryJSONField(null=True)
    slabs = BinaryJSONField(null=True)
    trade_id = UUIDField(null=True)
    procured_by_id=UUIDField(null=True)
    procured_by=BinaryJSONField(null=True)
    sourced_by_id=UUIDField(null=True)
    sourced_by=BinaryJSONField(null=True)
    trade_type = CharField(null=True,index = True)
    updated_at = DateTimeField(default=datetime.datetime.now())

    class Meta:
        table_name = 'air_freight_storage_rates'

    
    def validate_commodity(self):
        if self.commodity not in LOCAL_COMMODITIES:
            raise HTTPException(status_code = 404,details = 'Invalid Commodity')
    
    def validate_trade_type(self):
        if self.trade_type not in TRADE_TYPES:
            raise HTTPException(status_code = 404,details = 'Invalid Trade Type')
    
    def validate_free_limit(self):
        if not self.free_limit:
            raise HTTPException(status_code = 404,details = 'Free Limit Cannot Be Empty')
    
    def validate_slabs(self):
        if self.slabs:
            slabs = self.slabs
            lower_limits=[]
            upper_limits=[]
            for slab in slabs:
                if slab['upper_limit']<=slab['lower_limit']:
                    raise HTTPException (status_code=400, detail='slabs invalid')
            for slab in slabs:
                lower_limits.append(slab['lower_limit'])
                upper_limits.append(slab['upper_limit'])
            
            if lower_limits[0] and lower_limits[0]<=self.free_limit:
                raise HTTPException (status_code=400, detail='lower limit should be greater than free limit')
            
            if any(int(upper_limits[i]) >= int(lower_limits[i + 1]) for i in range(len(upper_limits) - 1)):
                raise HTTPException (status_code=500,detail='invalid slabs')
        
    def validate_airport_id(self):
        obj = {"filters":{"id": [(str(self.airport_id))],'type':'airport'}}
        airport = maps.list_locations(obj)['list']
        if airport:
            airport =airport[0]
            self.airport = {key:value for key,value in airport.items() if key in ['id', 'name','display_name', 'type','port_code']}
            self.country_id = airport.get('country_id', None)
            self.trade_id = airport.get('trade_id', None)
            self.continent_id = airport.get('continent_id', None)
            self.location_ids = [uuid.UUID(str(x)) for x in [self.airport_id, self.country_id, self.trade_id] if x is not None]
        else:
            raise HTTPException(status_code=500,detail='Invalid airport')
        
    def validate_airline_id(self):
        airline_data = get_operators(id=self.airline_id,operator_type='airline')
        if (len(airline_data) != 0) and airline_data[0].get('operator_type') == 'airline':
            self.airline = airline_data[0]
            return True
        raise HTTPException(status_code = 400, details = 'Airline Id Is Not Valid')
    
    def validate_service_provider_id(self):
        service_provider_data = get_organization(id=str(self.service_provider_id))
        if (len(service_provider_data) != 0) and service_provider_data[0].get('account_type') == 'service_provider':
            self.service_provider = service_provider_data[0]
            return True
        raise HTTPException(status_code = 400, details = 'Service Provider Id Is Not Valid') 
    

    def update_foreign_objects(self):
        self.update_local_objects()
        self.update_freight_objects()
    
    def update_freight_objects(self):
        location_key = 'origin' if self.trade_type == 'export' else 'destination'
        if location_key == 'origin':
            kwargs = {
                'origin_storage_id':self.id
            }
        else:
            kwargs = {
                'destination_storage_id':self.id
            }
        t=AirFreightRate.update(**kwargs).where(
            AirFreightRate.airline_id == self.airline_id,
            AirFreightRate.service_provider_id == self.service_provider_id,
            AirFreightRate.commodity <<['general','express'] if self.commodity == 'general' else AirFreightRate.commodity == self.commodity,
            (eval("AirFreightRate.{}_airport_id".format(location_key)) == self.airport_id),
            (eval("AirFreightRate.{}_storage_id".format(location_key)) == None)
            )
        t.execute() 
    
    def update_local_objects(self):
        AirFreightRateLocal.update(storage_rate_id=self.id).where(
            AirFreightRateLocal.airport_id == self.airport_id,
            AirFreightRateLocal.airline_id == self.airline_id,
            AirFreightRateLocal.commodity == self.commodity,
            AirFreightRateLocal.trade_type == self.trade_type,
            AirFreightRateLocal.service_provider_id == self.service_provider_id
        ).execute()
    
    def update_special_attributes(self):
        self.is_slabs_missing = True if not self.slabs else False
    
    def detail(self):
        return{
            'storage_rate':{
                'free_limit':self.free_limit,
                'slabs': self.slabs,
                'is_slabs_missing' : self.is_slabs_missing,
                'remarks': self.remarks
            }
        }

    def validate(self):
        self.validate_free_limit()
        self.validate_trade_type()
        self.validate_commodity()
        self.validate_airport_id()
        self.validate_slabs()
        self.validate_airline_id()
        self.validate_service_provider_id()
        return True