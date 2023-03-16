from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from peewee import *
from playhouse.postgres_ext import *
from database.db_session import db
from fastapi import HTTPException
from configs.fcl_freight_rate_constants import FREIGHT_CONTAINER_COMMODITY_MAPPINGS
from rails_client import client
from libs.locations import list_locations
import datetime

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = db
        # constraints = [SQL('UNIQUE (port_id, trade_type, main_port_id, container_size, container_type, commodity, shipping_line_id, source, task_type, service, status)')]

class FclFreightRateTask(BaseModel):
    commodity = CharField(index=True, null=True)
    completed_at = CharField(null=True)
    completed_by_id = CharField(null=True)
    completed_by = BinaryJSONField(null=True)
    completion_data = JSONField(null=True)
    container_size = CharField(index=True, null=True)
    container_type = CharField(index=True, null=True)
    country_id = UUIDField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    job_data = JSONField(null=True)
    location_ids = ArrayField(field_class=UUIDField, null=True)
    main_port_id = UUIDField(index=True, null=True)
    main_port = BinaryJSONField(null=True)
    port_id = UUIDField(index=True, null=True)
    port = BinaryJSONField(null=True)
    service = CharField(null=True)
    shipping_line_id = UUIDField(index=True, null=True)
    shipping_line = BinaryJSONField(null=True)
    shipment_serial_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::character varying[]")], field_class=CharField, null=True)
    source = CharField(null=True)
    source_count = IntegerField(null=True)
    status = CharField(null=True)
    task_type = CharField(null=True)
    trade_id = UUIDField(null=True)
    trade_type = CharField(null=True)
    updated_at = DateTimeField(default=datetime.datetime.now)
    
    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(FclFreightRateTask, self).save(*args, **kwargs)

    class Meta:
        table_name = 'fcl_freight_rate_tasks' 

    def validate_service(self):
        if self.service not in ['fcl_freight_local','subsidiary']:
            raise HTTPException(status_code=400, detail="Invalid service")
        
    def validate_port_id(self):
        obj = {"id": [(self.port_id)],'type':'seaport'}
        port = list_locations(obj)['list']
        if port:
            port =port[0]
            self.port = port
            self.country_id = port.get('country_id', None)
            self.trade_id = port.get('trade_id', None) 
            self.continent_id = port.get('continent_id', None)
            self.location_ids = [uuid.UUID(str(x)) for x in [self.port_id, self.country_id, self.trade_id, self.continent_id] if x is not None]
        else:
            raise HTTPException(status_code=500,detail='Invalid port')

    def validate_main_port_id(self):
        if self.port and self.port['is_icd']==False:
            if self.main_port_id and self.main_port_id!=self.port_id:
                raise HTTPException(status_code=500,detail='Invalid Main Port')
        elif self.port and self.port['is_icd']==True:
            main_port_data = list_locations({"id": [str(self.main_port_id)],'type':'seaport','is_icd':False})['list']
            if main_port_data:
                self.main_port = main_port_data[0]
            else:
                raise HTTPException(status_code=500,detail='Invalid Main Port')

    def validate_shipping_line_id(self):
        shipping_line_data = client.ruby.list_operators({'filters':{'id': [str(self.shipping_line_id)],'operator_type':'shipping_line'}})['list']
        if shipping_line_data:
            self.shipping_line = shipping_line_data[0]
        else:
            raise HTTPException(status_code=500,detail='invalid shipping line')
        
    def validate_task_type(self):
        if self.task_type not in ['locals_at_actuals', 'locals_purchase_invoice_review']:
            raise HTTPException(status_code=400, detail="Invalid task type")
        
    def validate_trade_type(self):
        if self.trade_type not in ['import', 'export', 'domestic']:
            raise HTTPException(status_code=400, detail="Invalid trade type")
        
    def validate_container_type(self):
        if self.container_type not in ['standard', 'refer', 'open_top', 'open_side', 'flat_rack', 'iso_tank']:
            raise HTTPException(status_code=400, detail="Invalid container type")
        
    def validate_container_size(self):
        if self.container_size not in ['20', '40', '40HC', '45HC']:
            raise HTTPException(status_code=400, detail="Invalid container size")
        
    def validate_commodity(self):
      if not (self.container_type and self.commodity in FREIGHT_CONTAINER_COMMODITY_MAPPINGS[f"{self.container_type}"]):
        raise HTTPException(status_code=400, detail="Invalid commodity")
    
    def validate_source(self):
        if self.source not in ['shipment', 'purchase_invoice', 'contract']:
            raise HTTPException(status_code=400, detail="Invalid source")
    
    def validate_status(self):
        if self.status not in ['pending', 'completed', 'aborted']:
            raise HTTPException(status_code=400, detail="Invalid status")
    
    def validate_job_data(self):
        if self.task_type == 'locals_purchase_invoice_review' and self.job_data is None:
            raise ValueError("job_data cannot be Empty for locals_purchase_invoice_review tasks")
    
    def validate_uniqueness(self):
        if self.status == 'pending' and FclFreightRateTask.select().where(
            (FclFreightRateTask.port_id == self.port_id) &
            (FclFreightRateTask.trade_type == self.trade_type) &
            (FclFreightRateTask.main_port_id == self.main_port_id) &
            (FclFreightRateTask.container_size == self.container_size) &
            (FclFreightRateTask.container_type == self.container_type) &
            (FclFreightRateTask.commodity == self.commodity) &
            (FclFreightRateTask.shipping_line_id == self.shipping_line_id) &
            (FclFreightRateTask.source == self.source) &
            (FclFreightRateTask.task_type == self.task_type) &
            (FclFreightRateTask.service == self.service) &
            (FclFreightRateTask.status == self.status)).count()!=0:
            raise ValueError("Record already exists with the given attributes")
        
    def validate(self):
        self.validate_service()
        self.validate_task_type()
        self.validate_trade_type()
        self.validate_container_type()
        self.validate_container_size()
        self.validate_commodity()
        self.validate_source()
        self.validate_status()
        self.validate_job_data()
        self.validate_uniqueness()
        self.validate_port_id()
        self.validate_main_port_id()
        self.validate_shipping_line_id()
        return True

    
