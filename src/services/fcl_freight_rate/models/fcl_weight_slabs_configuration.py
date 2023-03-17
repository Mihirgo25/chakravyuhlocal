from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
from rails_client import client
from fastapi import HTTPException
from configs.organization_constants import CATEGORY_TYPES
from configs.global_constants import CONTAINER_SIZES

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class FclWeightSlabsConfiguration(BaseModel):
    commodity = CharField(index=True, null=True)
    container_size = CharField(index=True, null=True)
    created_at = DateTimeField()
    currency = CharField()
    destination_location_id = UUIDField(index=True, null=True)
    destination_location_type = CharField(index=True, null=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    importer_exporter_id = UUIDField(index=True, null=True)
    is_cogo_assured = BooleanField(index=True, null=True)
    max_weight = DoubleField(index=True)
    organization_category = CharField(index=True, null=True)
    origin_location_id = UUIDField(index=True, null=True)
    origin_location_type = CharField(index=True, null=True)
    price = DoubleField()
    service_provider_id = UUIDField(index=True, null=True)
    shipping_line_id = UUIDField(index=True, null=True)
    slabs = BinaryJSONField(null = True)
    status = CharField(index=True)
    trade_type = CharField(index=True, null=True)
    updated_at = DateTimeField()

    class Meta:
        table_name = 'fcl_weight_slabs_configurations'
    
    def validate_origin_location_id(self):
        if not self.origin_location_id:
            pass
        
        location_data = client.ruby.list_locations({'id':self.origin_location_id})['list']
        if len(location_data) == 0:
            raise HTTPException(status_code=400, detail="Invalid location ID")
    
    def validate_destination_location_id(self):
        if not self.destination_location_id:
            pass
        
        location_data = client.ruby.list_locations({'id':self.destination_location_id})['list']
        if len(location_data) == 0:
            raise HTTPException(status_code=400, detail="Invalid location ID")

    def validate_origin_location_type(self):
        if not self.origin_location_type:
            pass
        
        if self.origin_location_type not in ['seaport', 'country']:
            raise HTTPException(status_code= 400, detail='Invalid Origin Location Type')
    
    def validate_destination_location_type(self):
        if not self.destination_location_type:
            pass
        
        if self.destination_location_type not in ['seaport', 'country']:
            raise HTTPException(status_code= 400, detail='Invalid Destination Location Type')

    def validate_organization_category(self):
        if not self.organization_category:
            pass
        
        if self.organization_category not in CATEGORY_TYPES:
            raise HTTPException(status_code = 400, detail = 'Invalid Organization Type')
    
    def validate_shipping_line_id(self):
        if not self.shipping_line_id:
            pass
        
        shipping_line_data = client.ruby.list_operators({'id':self.shipping_line_id})['list']
        if len(shipping_line_data) == 0:
            raise HTTPException(status_code=400, detail="Invalid shipping line ID")
    
    def validate_service_provider_id(self):
        if not self.service_provider_id:
            pass
        
        service_provider_data = client.ruby.list_organizations({'id':self.service_provider_id})['list']
        if len(service_provider_data) == 0:
            raise HTTPException(status_code=400, detail="Invalid service provider ID")
    
    def validate_importer_exporter_id(self):
        if not self.importer_exporter_id:
            pass
        
        importer_exporter_data = client.ruby.list_organizations({'id':self.importer_exporter_id})['list']
        if len(importer_exporter_data) == 0:
            raise HTTPException(status_code=400, detail="Invalid importer exporter ID")

    def validate_container_size(self):
        if not self.container_size:
            pass
        
        if self.container_size not in CONTAINER_SIZES:
            raise HTTPException(status_code=400, detail="Invalid container size")
            
    def validate_status(self):
        if not self.status:
            pass
        
        if self.status not in ['inactive', 'active']:
            raise HTTPException(status_code=400, detail="Invalid status")
    
    def validate_trade_type(self):
        if not self.trade_type:
            pass
        
        if self.status not in ['import', 'export']:
            raise HTTPException(status_code=400, detail="Invalid trade type")

    def validate(self):
        self.validate_origin_location_id()
        self.validate_destination_location_id()
        self.validate_origin_location_type()
        self.validate_destination_location_type()
        self.validate_organization_category()
        self.validate_shipping_line_id()
        self.validate_service_provider_id()
        self.validate_importer_exporter_id()
        self.validate_container_size()
        self.validate_status()
        self.validate_trade_type()
        return True
