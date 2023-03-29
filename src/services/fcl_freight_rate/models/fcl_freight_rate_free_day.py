from peewee import *
import datetime
from database.db_session import db
from playhouse.postgres_ext import *
from configs.fcl_freight_rate_constants import SPECIFICITY_TYPE, FREE_DAYS_TYPES, TRADE_TYPES, CONTAINER_SIZES, CONTAINER_TYPES, LOCATION_HIERARCHY
from fastapi import HTTPException
from params import Slab
from micro_services.client import *
from database.rails_db import *
from micro_services.client import maps

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class FclFreightRateFreeDay(BaseModel):
    container_size = CharField(index=True, null=True)
    container_type = CharField(index=True, null=True)
    continent_id = UUIDField(null=True)
    country_id = UUIDField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    free_days_type = CharField(index=True, null=True)
    free_limit = IntegerField(null=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    importer_exporter_id = UUIDField(null=True)
    importer_exporter = BinaryJSONField(null=True)
    is_slabs_missing = BooleanField(null=True)
    location_id = UUIDField(index=True, null=True)
    location = BinaryJSONField(null=True)
    location_type = CharField(index=True, null=True)
    port_id = UUIDField(null=True)
    previous_days_applicable = BooleanField(null=True)
    rate_not_available_entry = BooleanField(null=True)
    remarks = ArrayField(constraints=[SQL("DEFAULT '{}'::character varying[]")], field_class=CharField, null=True)
    service_provider_id = UUIDField(index=True, null=True)
    service_provider = BinaryJSONField(null=True)
    shipping_line_id = UUIDField(index=True, null=True)
    shipping_line = BinaryJSONField(null=True)
    slabs = BinaryJSONField(null=True)
    specificity_type = CharField(index=True, null=True)
    trade_id = UUIDField(null=True)
    trade_type = CharField(index=True, null=True)
    updated_at = DateTimeField(default=datetime.datetime.now())
    validity_start = DateTimeField(index=True, null=True, default=datetime.datetime.now())
    validity_end = DateTimeField(index=True, null=True, default=datetime.datetime.now() + datetime.timedelta(days=90))
    sourced_by_id = UUIDField(null=True)
    sourced_by = BinaryJSONField(null=True)
    procured_by_id = UUIDField(null=True)
    procured_by = BinaryJSONField(null=True)

    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(FclFreightRateFreeDay, self).save(*args, **kwargs)

    class Meta:
        table_name = 'fcl_freight_rate_free_days'

    def validate_location_ids(self):

        location_data = maps.list_locations({'filters':{'id': str(self.location_id)}})['list']
        if (len(location_data) != 0) and location_data[0].get('type') in ['seaport', 'country', 'trade', 'continent']:
            location_data = location_data[0]
            self.location = location_data
            self.port_id = location_data.get('seaport_id', None)
            self.country_id = location_data.get('country_id', None)
            self.trade_id = location_data.get('trade_id', None)
            self.continent_id = location_data.get('continent_id', None)
            self.location_type = 'port' if location_data.get('type') == 'seaport' else location_data.get('type')
            self.location = {key:value for key,value in location_data.items() if key in ['id', 'name', 'display_name', 'port_code', 'type']}

            return True
        return False

    def validate_specificity_type(self):
        if self.specificity_type and self.specificity_type in SPECIFICITY_TYPE:
            return True
        return False

    def validate_shipping_line(self):
        shipping_line_data = get_shipping_line(str(self.shipping_line_id))
        if (len(shipping_line_data) != 0) and shipping_line_data[0].get('operator_type') == 'shipping_line':
            self.shipping_line = shipping_line_data[0]
            return True
        return False

    def validate_service_provider(self):
        service_provider_data = get_service_provider(str(self.service_provider_id))
        if (len(service_provider_data) != 0) and service_provider_data[0].get('account_type') == 'service_provider':
            self.service_provider = service_provider_data[0]
            return True
        return False

    def validate_importer_exporter(self):
        if self.importer_exporter_id:
            importer_exporter_data = get_service_provider(str(self.importer_exporter_id))
            if (len(importer_exporter_data) != 0) and importer_exporter_data[0].get('account_type') == 'importer_exporter':
                self.importer_exporter = importer_exporter_data[0]
                return True
            return False
        return True

    def validate_free_days_type(self):
        if self.free_days_type and self.free_days_type in FREE_DAYS_TYPES:
            return True
        return False

    def validate_trade_type(self):
        if self.trade_type and self.trade_type in TRADE_TYPES:
            return True
        return False

    def validate_container_size(self):
        if self.container_size and self.container_size in CONTAINER_SIZES:
            return True
        return False

    def validate_container_type(self):
        if self.container_type and self.container_type in CONTAINER_TYPES:
            return True
        return False

    def validate_free_limit(self):
        if self.free_limit:
            return True
        return False

    def validate_before_save(self):
        if self.slabs:
            for slab in self.slabs:
                slab = Slab(**slab)
                try:
                    Slab.validate(slab)
                except:
                    raise HTTPException(status_code=422, detail=f"Incorrect Slab: {slab}")
        if not self.validate_location_ids():
            raise HTTPException(status_code=422, detail="Invalid location")   

        if not self.validate_specificity_type():
            raise HTTPException(status_code=422, detail="Invalid specificity type")

        if not self.validate_shipping_line():
            raise HTTPException(status_code=422, detail="Invalid shipping line")
        

        # if not self.validate_service_provider():
        #     raise HTTPException(status_code=422, detail="Invalid service provider")

        # if not self.validate_importer_exporter():
        #     raise HTTPException(status_code=422, detail="Invalid importer-exporter")

        if not self.validate_free_days_type():
            raise HTTPException(status_code=422, detail="Invalid free day type")
        

        if not self.validate_trade_type():
            raise HTTPException(status_code=422, detail="Invalid trade type")
        

        if not self.validate_container_size():
            raise HTTPException(status_code=422, detail="incorrect container size")
        

        if not self.validate_container_type():
            raise HTTPException(status_code=422, detail="Invalid container type")
        

        if not self.validate_free_limit():
            raise HTTPException(status_code=422, detail="Empty free limit")


    def update_special_attributes(self):
        self.is_slabs_missing = False if self.slabs and len(self.slabs) != 0 else True

    def detail(self):
        return {
            "free_day": {
                "id": self.id,
                "trade_type": self.trade_type,
                "free_days_type": self.free_days_type,
                "free_limit": self.free_limit,
                "remarks": self.remarks,
                "slabs": self.slabs,
                "is_slabs_missing": self.is_slabs_missing
            }
        }
    
    def validate_validity_object(self, validity_start, validity_end):
        if not validity_start:
            raise HTTPException(status_code=400, detail=validity_start + ' is invalid')

        if not validity_end:
            raise HTTPException(status_code=400, detail=validity_end + ' is invalid')

        if validity_end > (datetime.date.today() + datetime.timedelta(days = 180)):
            raise HTTPException(status_code=400, detail=validity_end + ' can not be greater than 60 days from current date')

        if validity_start < (datetime.date.today() - datetime.timedelta(days = 15)):
            raise HTTPException(status_code=400, detail=validity_start + ' can not be less than 15 days from current date')

        if validity_end < validity_start:
            raise HTTPException(status_code=400, detail=validity_end + ' can not be lesser than start validity')