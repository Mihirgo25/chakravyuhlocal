from peewee import *
from database.db_session import db
import uuid
import datetime
from playhouse.postgres_ext import BinaryJSONField, ArrayField
from fastapi import HTTPException
from micro_services.client import *
from params import LineItem




class BaseModel(Model):
    class Meta:
        database = db
class HaulageFreightRate(BaseModel):
    id = BigAutoField(primary_key=True)
    origin_location_id = UUIDField(null=True)
    origin_cluster_id = UUIDField(null=True)
    origin_city_id = UUIDField(null=True)
    destination_location_id = UUIDField(null=True)
    destination_cluster_id = UUIDField(null=True)
    destination_city_id = UUIDField(null=True)
    container_size = CharField(index=True, null=True)
    commodity_type = CharField(index=True, null=True)
    commodity = CharField(index=True, null=True)
    importer_exporter_id = UUIDField(null=True)
    service_provider_id = UUIDField(null=True)
    containers_count =  IntegerField(index=True, null=True)
    container_type = CharField(index=True, null=True)
    weight_slabs = BinaryJSONField(index=True, null=True)
    line_items = BinaryJSONField(index=True, null=True)
    is_line_items_error_messages_present = BooleanField(index=True, null=True)
    is_line_items_info_messages_present = BooleanField(index=True, null=True)
    line_items_error_messages = BinaryJSONField(index=True, null=True)
    line_items_info_messages = BinaryJSONField(index=True, null=True)
    rate_not_available_entry = BooleanField(index=True, null=True)
    trip_type = CharField(index=True, null=True)
    validity_start = DateTimeField(default=datetime.datetime.now)
    validity_end = DateTimeField(default = datetime.datetime.now() - datetime.timedelta(30))
    detention_free_time = IntegerField(index=True, null=True)
    transit_time = IntegerField(index=True, null=True)
    haulage_type = CharField(index=True, null=True, default='merchant')
    transport_modes =ArrayField(CharField, null=True)
    destination_country_id = UUIDField(null=True)
    transport_modes_keyword = CharField(index=True, null=True)
    distance = FloatField(null=True, index=True)
    origin_country_id = UUIDField(null=True)
    shipping_line_id = UUIDField(null=True)
    origin_destination_location_type = CharField(index=True, null=True)
    destination_location_type = CharField(index=True, null=True)
    origin_location_type = CharField(index=True, null=True)
    origin_location_ids = ArrayField(UUIDField, null=True)
    destination_location_ids = ArrayField(UUIDField, null=True)
    importer_exporter = BinaryJSONField(index=True, null=True)
    service_provider = BinaryJSONField(index=True, null=True)
    origin_location = BinaryJSONField(index=True, null=True)
    destination_location = BinaryJSONField(index=True, null=True)
    shipping_line = BinaryJSONField(index=True, null=True)
    validities = BinaryJSONField(default = [], null=True)
    created_at = DateTimeField(default=datetime.datetime.now, index=True)
    updated_at = DateTimeField(default=datetime.datetime.now, index=True)

    class Meta:
        table_name = 'haulage_freight_rates'

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(HaulageFreightRate, self).save(*args, **kwargs)
    
    def set_origin_location_ids(self):
        self.origin_cluster_id = self.origin_location.get('cluster_id')
        self.origin_city_id = self.origin_location.get('city_id')
        self.origin_country_id = self.origin_location.get('country_id')
        self.origin_location_ids = [uuid.UUID(str(self.origin_location_id)), uuid.UUID(str(self.origin_cluster_id)),uuid.UUID(str(self.origin_city_id)),uuid.UUID(str(self.origin_country_id))]

    def set_origin_location_type(self):
        self.origin_location_type = self.origin_location.get('type')

    def set_destination_location_ids(self):
        self.destination_cluster_id = self.destination_location.get('cluster_id')
        self.destination_city_id = self.destination_location.get('city_id')
        self.destination_country_id = self.destination_location.get('country_id')
        self.destination_location_ids = [uuid.UUID(str(self.destination_location_id)), uuid.UUID(str(self.destination_cluster_id)),uuid.UUID(str(self.destination_city_id)),uuid.UUID(str(self.destination_country_id))]


    def set_destination_location_type(self):
        self.destination_location_type = self.destination_location.get('type')

    def set_origin_destination_location_type(self):
        self.origin_destination_location_type = ':'.join([str(self.origin_location_type),str(self.destination_location_type)])

    def validate_duplicate_line_items(self):
        self.line_items = self.line_items or []
        if len(set(map(lambda t: str(t['code']).upper(), self.line_items))) != len(self.line_items):
            raise HTTPException(status_code=500, detail="Contains Duplicates")
        
    def validate_invalid_line_items(self,possible_charge_codes):
        invalid_line_items = [str(line_item.get('code') or '') for line_item in self.line_items if str(line_item.get('code') or '').strip() not in possible_charge_codes]
        if invalid_line_items:
            raise HTTPException(status_code=500, detail= ','.join(invalid_line_items))
        

    def validate_validity_object(self, validity_start, validity_end):
        if self.transport_modes[0] != 'trailer':
            return
        
        if not validity_start:
            raise HTTPException(status_code=400, detail="validity_start is invalid")
        
        if not validity_end:
            raise HTTPException(status_code=400, detail="validity_end is invalid")

        if validity_end < validity_start:
            raise HTTPException(status_code=400, detail="validity_end can not be lesser than validity_start")
      
    def get_mandatory_line_items(self,mandatory_charge_codes):
        mandatory_line_items = [line_item for line_item in self.line_items if str((line_item.get('code') or '').upper()) in mandatory_charge_codes]
        return mandatory_line_items
    

    def set_platform_price(self,mandatory_charge_codes,currency):
        line_items = self.get_mandatory_line_items(mandatory_charge_codes)

        if not line_items:
            return
        result = self.get_line_items_total_price(line_items)

        rates = HaulageFreightRate.select().where(
            HaulageFreightRate.origin_location_id == self.origin_location_id,
            HaulageFreightRate.destination_location_id == self.destination_location_id,
            HaulageFreightRate.container_size == self.container_size,
            HaulageFreightRate.container_type == self.container_type,
            HaulageFreightRate.commodity == self.commodity,
            HaulageFreightRate.shipping_line_id == self.shipping_line_id,
            HaulageFreightRate.haulage_type == self.haulage_type,
            HaulageFreightRate.transit_time == self.transit_time,
            HaulageFreightRate.detention_free_time == self.detention_free_time,
            HaulageFreightRate.trip_type == self.trip_type,
            # HaulageFreightRate.trailer_type == self.trailer_type,
            HaulageFreightRate.is_line_items_error_messages_present == False,
            HaulageFreightRate.service_provider_id != self.service_provider_id
        ).where(HaulageFreightRate.importer_exporter_id.in_([None, self.importer_exporter_id])).execute()

        sum = 0
        mandatory_line_items = [line_item for line_item in self.line_items if str((line_item.get('code') or '').upper()) in mandatory_charge_codes]

        for prices in mandatory_line_items:
                sum = sum + int(common.get_money_exchange_for_fcl({'price': prices["price"], 'from_currency': prices['currency'], 'to_currency':currency})['price'])

        if sum and result > sum:
            result = sum

        self.validities['platform_price'] = result

    def get_line_items_total_price(self,line_items):
        currency = line_items[0].currency
        result = 0

        for line_item in line_items:
            result = result + int(common.get_money_exchange_for_fcl({'price': line_item["price"], 'from_currency': line_item['currency'], 'to_currency':currency})['price'])

        return result
       


        

class FclFreightRateValidity(BaseModel):
    validity_start: datetime.date
    validity_end: datetime.date
    remarks: list[str] = []
    line_items: list[LineItem] = []
    price: float
    platform_price: float = None
    currency: str
    schedule_type: str = None
    payment_term: str = None
    id: str
    likes_count: int = None
    dislikes_count: int = None