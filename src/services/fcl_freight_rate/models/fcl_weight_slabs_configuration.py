from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
from fastapi import HTTPException
from configs.organization_constants import CATEGORY_TYPES
from configs.global_constants import CONTAINER_SIZES
from micro_services.client import maps
import datetime
from database.rails_db import *

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class FclWeightSlabsConfiguration(BaseModel):
    commodity = CharField(index=True, null=True)
    container_size = CharField(index=True, null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    currency = CharField(null = True)
    destination_location_id = UUIDField(index=True, null=True)
    destination_location_type = CharField(index=True, null=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    importer_exporter_id = UUIDField(index=True, null=True)
    is_cogo_assured = BooleanField(null=True)
    max_weight = DoubleField(null = True)
    organization_category = CharField(index=True, null=True)
    origin_location_id = UUIDField(index=True, null=True)
    origin_location_type = CharField(index=True, null=True)
    price = DoubleField(null =True)
    service_provider_id = UUIDField(index=True, null=True)
    shipping_line_id = UUIDField(index=True, null=True)
    slabs = BinaryJSONField(null = True)
    status = CharField(index=True, null = True)
    trade_type = CharField(index=True, null=True)
    updated_at = DateTimeField(default=datetime.datetime.now, index = True)


    class Meta:
        table_name = 'fcl_weight_slabs_configurations'

    def validate_origin_location(self):
        if not self.origin_location_id:
            return

        location_data = maps.list_locations({'filters':{'id':self.origin_location_id}})['list']
        if len(location_data) == 0:
            raise HTTPException(status_code=400, detail="Invalid Origin location ID")
        if self.origin_location_type not in ['seaport', 'country'] or self.origin_location_type != location_data[0]['type']:
            raise HTTPException(status_code= 422, detail='Invalid Origin Location Type')


    def validate_destination_location(self):
        if not self.destination_location_id:
            return

        location_data = maps.list_locations({'filters':{'id':self.destination_location_id}})['list']
        if len(location_data) == 0:
            raise HTTPException(status_code=400, detail="Invalid location ID")

    # def validate_origin_location_type(self):
    #     if not self.origin_location_type:
    #         return

    #     if :
    #         raise HTTPException(status_code= 422, detail='Invalid Origin Location Type')

    # def validate_destination_location_type(self):
    #     if not self.destination_location_type:
    #         return

    #     if self.destination_location_type not in ['seaport', 'country']:
    #         raise HTTPException(status_code= 422, detail='Invalid Destination Location Type')

    def validate_organization_category(self):
        if not self.organization_category:
            return

        if self.organization_category not in CATEGORY_TYPES:
            raise HTTPException(status_code = 422, detail = 'Invalid Organization Category')

    def validate_shipping_line_id(self):
        if not self.shipping_line_id:
            return

        shipping_line_data = get_operators(id=self.shipping_line_id)
        if len(shipping_line_data) == 0:
            raise HTTPException(status_code=400, detail="Invalid shipping line ID")

    def validate_service_provider_id(self):
        if not self.service_provider_id:
            return

        service_provider_data = get_organization(id=self.service_provider_id)
        if len(service_provider_data) == 0:
            raise HTTPException(status_code=400, detail="Invalid service provider ID")

    def validate_importer_exporter_id(self):
        if not self.importer_exporter_id:
            return

        importer_exporter_data = get_organization(id=self.importer_exporter_id)
        if len(importer_exporter_data) == 0:
            raise HTTPException(status_code=400, detail="Invalid importer exporter ID")

    def validate_container_size(self):
        if not self.container_size:
            return

        if self.container_size not in CONTAINER_SIZES:
            raise HTTPException(status_code=400, detail="Invalid container size")

    def validate_status(self):
        if self.status not in ['inactive', 'active']:
            raise HTTPException(status_code=400, detail="Invalid status")

    def validate_trade_type(self):
        if not self.trade_type:
            return

        if self.trade_type not in ['import', 'export']:
            raise HTTPException(status_code=400, detail="Invalid trade type")

    def validate(self):
        self.validate_origin_location()
        self.validate_destination_location()
        # self.validate_origin_location_type()
        # self.validate_destination_location_type()
        self.validate_organization_category()
        self.validate_shipping_line_id()
        self.validate_service_provider_id()
        self.validate_importer_exporter_id()
        self.validate_container_size()
        self.validate_status()
        self.validate_trade_type()
        return True
