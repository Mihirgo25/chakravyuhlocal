from peewee import *
from rails_client import client
import datetime
from database.db_session import db
from playhouse.postgres_ext import *
from configs.fcl_freight_rate_constants import CONTAINER_SIZES, CONTAINER_TYPES, LOCATION_PAIR_HIERARCHY
from fastapi import HTTPException
from params import Slab


class BaseModel(Model):
    class Meta:
        database = db

class FclFreightRateWeightLimit(BaseModel):
    container_size = CharField(null=True)
    container_type = CharField(index=True, null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    destination_continent_id = UUIDField(index=True, null=True)
    destination_country_id = UUIDField(index=True, null=True)
    destination_location_id = UUIDField(null=True)
    destination_location_type = CharField(null=True)
    destination_port_id = UUIDField(index=True, null=True)
    destination_trade_id = UUIDField(index=True, null=True)
    free_limit = DoubleField(null=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    is_slabs_missing = BooleanField(null=True)
    origin_continent_id = UUIDField(index=True, null=True)
    origin_country_id = UUIDField(index=True, null=True)
    origin_destination_location_type = CharField(index=True, null=True)
    origin_location_id = UUIDField(null=True)
    origin_location_type = CharField(null=True)
    origin_port_id = UUIDField(index=True, null=True)
    origin_trade_id = UUIDField(index=True, null=True)
    remarks = ArrayField(constraints=[SQL("DEFAULT '{}'::character varying[]")], field_class=CharField, null=True)
    service_provider_id = UUIDField(null=True)
    shipping_line_id = UUIDField(index=True, null=True)
    slabs = BinaryJSONField(null=True)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = 'fcl_freight_rate_weight_limits'
        indexes = (
            (('container_size', 'container_type'), False),
            (('origin_location_id', 'destination_location_id', 'container_size', 'container_type', 'shipping_line_id', 'service_provider_id'), True),
            (('service_provider_id', 'shipping_line_id', 'container_size', 'container_type'), False),
            (('updated_at', 'service_provider_id', 'is_slabs_missing'), False),
            (('updated_at', 'service_provider_id', 'shipping_line_id', 'is_slabs_missing'), False),
        )

    def validate_location_ids(self):
        LOCATION_TYPES = ('seaport', 'country', 'trade', 'continent')
        params = {"filters" : {"id": [str(self.origin_location_id), str(self.destination_location_id)]}}
        location_data = client.ruby.list_locations(params)['list']

        if len(location_data) != 0:
            count = 0
            for location in location_data:
                if location['id'] == str(self.origin_location_id) and location['type'] in LOCATION_TYPES:
                    self.origin_location = location

                    self.origin_port_id = location.get('seaport_id', None)
                    self.origin_country_id = location.get('country_id', None)
                    self.origin_trade_id = location.get('trade_id', None)
                    self.origin_continent_id = location.get('continent_id', None)

                    self.origin_location_type = 'port' if location.get('type') == 'seaport' else location.get('type')
                    count += 1

                elif location['id'] == str(self.destination_location_id) and location['type'] in LOCATION_TYPES:
                    self.destination_location = location

                    self.destination_port_id = location.get('seaport_id', None)
                    self.destination_country_id = location.get('country_id', None)
                    self.destination_trade_id = location.get('trade_id', None)
                    self.destination_continent_id = location.get('continent_id', None)

                    self.destination_location_type = 'port' if location.get('type') == 'seaport' else location.get('type')
                    self.origin_destination_location_type = str(self.origin_location_type) + ':' + str(self.destination_location_type)
                    count += 1
            if count == 2:
                return True
        return False

    def validate_shipping_line(self):
        shipping_line_data = client.ruby.list_operators({'filters':{'id': str(self.shipping_line_id)}})['list']
        if len(shipping_line_data)!= 0 and shipping_line_data[0].get('operator_type') == 'shipping_line':
            return True
        return False

    def validate_service_provider(self):
        service_provider_data = client.ruby.list_organizations({'filters':{'id': str(self.service_provider_id)}})['list']
        if len(service_provider_data) != 0 and service_provider_data[0].get('account_type') == 'service_provider':
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

    def valid_uniqueness(self):
        freight_weight_limit_cnt = FclFreightRateWeightLimit.select().where(
            FclFreightRateWeightLimit.origin_location_id == self.origin_location_id,
            FclFreightRateWeightLimit.destination_location_id == self.destination_location_id,
            FclFreightRateWeightLimit.container_size == self.container_size,
            FclFreightRateWeightLimit.container_type == self.container_type,
            FclFreightRateWeightLimit.shipping_line_id == self.shipping_line_id,
            FclFreightRateWeightLimit.service_provider_id == self.service_provider_id
        ).count()

        if self.id and freight_weight_limit_cnt==1:
            return True
        if not self.id and freight_weight_limit_cnt==0:
            return True
        return False

    def validate_free_limit(self):
      if self.free_limit:
        return True
      return False

    def validate_slabs(self):
        if self.slabs:
            for slab in self.slabs:
                slab = Slab(**slab)
                try:
                    Slab.validate(slab)
                except:
                    raise HTTPException(status_code=499, detail=f"Incorrect Slab: {slab}")

            slabs = sorted(self.slabs, key=lambda slab:slab['lower_limit'])

            if len(slabs) != 0 and float(self.free_limit) != 0 and (float(self.free_limit) > float(slabs[0]['lower_limit'])):
                raise (slabs, 'lower limit should be greater than free limit')
            
            for index, slab in enumerate(slabs):
                if (float(slab['upper_limit']) <= float(slab['lower_limit'])) or (index != 0 and float(slab['lower_limit']) <= float(slabs[index - 1]['upper_limit'])):
                        raise (slabs, 'invalid')
            return True
        return True

    def validate_before_save(self):
        
        if not self.validate_location_ids():
            raise HTTPException(status_code=499, detail="Invalid location")
        print('1')
        if not self.validate_shipping_line():
            raise HTTPException(status_code=499, detail="Invalid shipping line")
        print('2')
        if not self.validate_service_provider():
            raise HTTPException(status_code=499, detail="Invalid service provider")
        print('3')
        if not self.validate_container_size():
            raise HTTPException(status_code=499, detail="Incorrect container size")
        print('4')
        if not self.validate_container_type():
            raise HTTPException(status_code=499, detail="Invalid container type")
        print('5')
        if not self.validate_free_limit():
            raise HTTPException(status_code=499, detail="Empty free limit")
        print('6')
        if not self.valid_uniqueness():
            raise HTTPException(status_code=499, detail="Violates uniqueness validation")
        print('7')
        if not self.validate_slabs():
            raise HTTPException(status_code=499, detail="Incorrect slabs")
        print('8')

    def update_special_attributes(self):
        self.update(is_slabs_missing = False) if self.slabs and len(self.slabs) != 0 else self.update(is_slabs_missing = True)

    def detail(self):
      return {
        "weight_limit": {
            "id": self.id,
            "free_limit": self.free_limit,
            "remarks": self.remarks,
            "slabs": self.slabs,
            "is_slabs_missing": self.is_slabs_missing,
        }
    }