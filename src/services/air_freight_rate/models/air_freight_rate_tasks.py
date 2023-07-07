from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
import datetime
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from services.air_freight_rate.constants.air_freight_rate_constants import COMMODITY , COMMODITY_TYPE
from micro_services.client import * 
from database.rails_db import *

from fastapi import HTTPException
from configs.definitions import AIR_FREIGHT_SURCHARGES


class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class AirFreightRateTasks(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    service = CharField(index=True,null=True)
    airport_id = UUIDField(index=True,null=True)
    airport = BinaryJSONField(null=True)
    country_id=UUIDField(null=True)
    trade_id=UUIDField(null=True)
    location_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, index=True, null=True)
    commodity=CharField(null=True,index = True)
    commodity_type=CharField(null=True,index=True)
    logistics_service_type=CharField(null=True,index=True)
    trade_type=CharField(null=True,index=True)
    airline_id=UUIDField(index=True,null=True)
    airline=BinaryJSONField(null=True)
    source=CharField(null=True)
    source_count=IntegerField(null=True)
    task_type=CharField(null=True)
    status=CharField(null=True,index = True)
    completion_data=BinaryJSONField(null=True)
    completed_at=DateTimeField(default=datetime.datetime.now(),null=True)
    completed_by_id=UUIDField(null=True,index=True)
    completed_by=BinaryJSONField(null=True)
    created_at=DateTimeField(default=datetime.datetime.now(),null=True)
    updated_at=DateTimeField(default=datetime.datetime.now(),null=True)
    job_data=BinaryJSONField(null=True)
    shipment_serial_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::character varying[]")], field_class=CharField, null=True)


    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(AirFreightRateTasks, self).save(*args, **kwargs)

    class Meta:
        table_name = 'air_freight_rate_tasks'
    

    def validate_service(self):
        if self.service:
            if self.service not in ['air_freight_local']:
                raise HTTPException (status_code=400, detail='Invalid Service')
        
    def validate_task_type(self):
        if self.task_type not in ['locals_at_actuals', 'locals_purchase_invoice_review']:
            raise HTTPException(status_code=400,detail='Invalid Task Type')
    
    def validate_trade_type(self):
        if self.trade_type not in ['import', 'export', 'domestic']:
            raise HTTPException(status_code=400,detail="Invalid trade type")
    
    def validate_commodity(self):
        if self.commodity not in COMMODITY:
            raise HTTPException(status_code=400, detail='Invalid Commodity')
    
    def validate_commodity_type(self):
        if self.commodity_type not in COMMODITY_TYPE:
            raise HTTPException(status_code=400, detail='Invalid Commodity TYPE')
    
    def validate_source(self):
        if self.source:
            if self.source not in ['shipment', 'purchase_invoice', 'contract']:
                raise HTTPException (status_code=400,detail="invalid source")

    def validate_status(self):
        if self.status not in ['pending', 'completed', 'aborted']:
            raise HTTPException(status_code=400, detail='invalid status')
    
    def validate_job_data(self):
        if self.task_type == 'locals_purchase_invoice_review' and self.job_data is None:
            raise ValueError("job_data cannot be Empty for locals_purchase_invoice_review tasks")
        
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
        airline_data = get_operators(id=str(self.airline_id))
        if airline_data:
            self.airline = airline_data[0]
        else:
            raise HTTPException(status_code=500,detail='invalid air line')
        
    
    def validate(self):
        self.validate_service()
        self.validate_task_type()
        self.validate_trade_type()
        self.validate_commodity()
        self.validate_commodity_type()
        self.validate_source()
        self.validate_status()
        self.validate_job_data()
        self.validate_airport_id()
        self.validate_airline_id()
        return True