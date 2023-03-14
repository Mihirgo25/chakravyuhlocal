from peewee import *
from rails_client import client
import datetime
from database.db_session import db
from playhouse.postgres_ext import *
from configs.fcl_freight_rate_constants import SPECIFICITY_TYPE, FREE_DAYS_TYPES, TRADE_TYPES, CONTAINER_SIZES, CONTAINER_TYPES, LOCATION_HIERARCHY
from playhouse.shortcuts import model_to_dict
from fastapi import HTTPException
from params import Slab


class BaseModel(Model):
    class Meta:
        database = db

class FclFreightRateFreeDay(BaseModel):
    container_size = CharField(null=True)
    container_type = CharField(index=True, null=True)
    continent_id = UUIDField(index=True, null=True)
    country_id = UUIDField(index=True, null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    free_days_type = CharField(index=True, null=True)
    free_limit = IntegerField(null=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    importer_exporter_id = UUIDField(null=True)
    is_slabs_missing = BooleanField(null=True)
    location_id = UUIDField(null=True)
    location_type = CharField(index=True, null=True)
    port_id = UUIDField(index=True, null=True)
    previous_days_applicable = BooleanField(null=True)
    rate_not_available_entry = BooleanField(null=True)
    remarks = ArrayField(constraints=[SQL("DEFAULT '{}'::character varying[]")], field_class=CharField, null=True)
    service_provider_id = UUIDField(null=True)
    shipping_line_id = UUIDField(index=True, null=True)
    slabs = BinaryJSONField(null=True)
    specificity_type = CharField(null=True)
    trade_id = UUIDField(index=True, null=True)
    trade_type = CharField(index=True, null=True)
    updated_at = DateTimeField(default=datetime.datetime.now)
    
    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(FclFreightRateFreeDay, self).save(*args, **kwargs)

    class Meta:
        table_name = 'fcl_freight_rate_free_days'
        indexes = (
            (('container_size', 'container_type'), False),
            (('importer_exporter_id', 'service_provider_id'), False),
            (('rate_not_available_entry', 'location_id', 'trade_type', 'free_days_type', 'container_size', 'container_type', 'shipping_line_id', 'service_provider_id', 'specificity_type', 'importer_exporter_id'), False),
            (('service_provider_id', 'shipping_line_id', 'container_size', 'container_type', 'free_days_type', 'port_id'), False),
            (('service_provider_id', 'shipping_line_id', 'container_size', 'container_type', 'port_id'), False),
            (('service_provider_id', 'shipping_line_id', 'container_size', 'container_type', 'trade_type', 'free_days_type', 'port_id'), False),
            (('updated_at', 'id', 'service_provider_id'), False),
            (('updated_at', 'service_provider_id'), False),
            (('updated_at', 'service_provider_id', 'free_days_type', 'is_slabs_missing'), False),
            (('updated_at', 'service_provider_id', 'free_days_type', 'port_id'), False),
            (('updated_at', 'service_provider_id', 'free_days_type', 'shipping_line_id', 'is_slabs_missing'), False),
            (('updated_at', 'service_provider_id', 'free_days_type', 'trade_type', 'is_slabs_missing'), False),
            (('updated_at', 'service_provider_id', 'is_slabs_missing'), False),
            (('updated_at', 'service_provider_id', 'port_id'), False),
            (('updated_at', 'service_provider_id', 'shipping_line_id', 'is_slabs_missing'), False),
            (('updated_at', 'service_provider_id', 'trade_type', 'is_slabs_missing'), False),
        )

    def validate_location_ids(self):

        location_data = client.ruby.list_locations({'filters':{'id': str(self.location_id)}})['list']

        if (len(location_data) != 0) and location_data[0].get('type') in ['seaport', 'country', 'trade', 'continent']:
            location_data = location_data[0]

            self.location = location_data
            self.port_id = location_data.get('seaport_id', None)
            self.country_id = location_data.get('country_id', None)
            self.trade_id = location_data.get('trade_id', None)
            self.continent_id = location_data.get('continent_id', None)
            self.location_type = 'port' if location_data.get('type') == 'seaport' else location_data.get('type')

            return True
        return False

    def validate_specificity_type(self):
        if self.specificity_type and self.specificity_type in SPECIFICITY_TYPE:
            return True
        return False

    def validate_shipping_line(self):
        shipping_line_data = client.ruby.list_operators({'filters': {'id': str(self.shipping_line_id)}})['list']
        if (len(shipping_line_data) != 0) and shipping_line_data[0].get('operator_type') == 'shipping_line':
            self.shipping_line = shipping_line_data[0]
            return True
        return False

    def validate_service_provider(self):
        service_provider_data = client.ruby.list_organizations({'filters': {'id': str(self.service_provider_id)}})['list']
        if (len(service_provider_data) != 0) and service_provider_data[0].get('account_type') == 'service_provider':
            self.service_provider = service_provider_data[0]
            return True
        return False

    def validate_importer_exporter(self):
        if self.importer_exporter_id:
            importer_exporter_data = client.ruby.list_organizations({'filters': {'id': str(self.importer_exporter_id)}})['list']
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

    def validate_uniqueness(self):
        freight_free_day_cnt = FclFreightRateFreeDay.select().where(
            FclFreightRateFreeDay.location_id == self.location_id,
            FclFreightRateFreeDay.trade_type == self.trade_type,
            FclFreightRateFreeDay.free_days_type == self.free_days_type,
            FclFreightRateFreeDay.container_size == self.container_size,
            FclFreightRateFreeDay.container_type == self.container_type,
            FclFreightRateFreeDay.shipping_line_id == self.shipping_line_id,
            FclFreightRateFreeDay.service_provider_id == self.service_provider_id,
            FclFreightRateFreeDay.importer_exporter_id == self.importer_exporter_id,
            FclFreightRateFreeDay.specificity_type == self.specificity_type
        ).count()

        if self.id and freight_free_day_cnt == 1:
            return True
        if not self.id and freight_free_day_cnt == 0:
            return True

        return False

    def validate_before_save(self):
        if self.slabs:
            for slab in self.slabs:
                slab = Slab(**slab)
                try:
                    Slab.validate(slab)
                except:
                    raise HTTPException(status_code=499, detail=f"Incorrect Slab: {slab}")

        if not self.validate_location_ids():
            raise HTTPException(status_code=499, detail="Invalid location")

        if not self.validate_specificity_type():
            raise HTTPException(status_code=499, detail="Invalid specificity type")

        if not self.validate_shipping_line():
            raise HTTPException(status_code=499, detail="Invalid shipping line")

        if not self.validate_service_provider():
            raise HTTPException(status_code=499, detail="Invalid service provider")

        if not self.validate_importer_exporter():
            raise HTTPException(status_code=499, detail="Invalid importer-exporter")

        if not self.validate_free_days_type():
            raise HTTPException(status_code=499, detail="Invalid free day type")

        if not self.validate_trade_type():
            raise HTTPException(status_code=499, detail="Invalid trade type")

        if not self.validate_container_size():
            raise HTTPException(status_code=499, detail="incorrect container size")

        if not self.validate_container_type():
            raise HTTPException(status_code=499, detail="Invalid container type")

        if not self.validate_free_limit():
            raise HTTPException(status_code=499, detail="Empty free limit")

        if not self.validate_uniqueness():
            raise HTTPException(status_code=499, detail='violates uniqueness validation')

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
                "is_slabs_missing": self.is_slabs_missing,
            }
        }
