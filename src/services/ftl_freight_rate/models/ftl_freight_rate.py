import re, datetime
from peewee import *
from fastapi import HTTPException
from database.db_session import db
from playhouse.postgres_ext import *
from configs.ftl_freight_rate_constants import RATE_TYPES, BODY_TYPE, TRIP_TYPES, VALID_UNITS, COMMODITIES
from micro_services.client import maps

class UnknownField(object): 
    def __init__(self, *_, **__): pass

class BaseModel(Model): 
    class Meta:
        database = db
        only_save_dirty = True

class FtlFreightRate(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    origin_location_id = UUIDField(null=True, index=True)
    origin_cluster_id = UUIDField(null=True, index=True)
    origin_country_id = UUIDField(null=True, index=True)
    origin_city_id = UUIDField(null=True, index=True)
    origin_location_type = CharField(null=True, index=True)
    origin_location_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, index=True, null=True)
    destination_location_id = UUIDField(null=True, index=True)
    destination_cluster_id = UUIDField(null=True, index=True)
    destination_country_id = UUIDField(null=True, index=True)
    destination_city_id = UUIDField(null=True, index=True)
    destination_location_type = CharField(null=True, index=True)
    destination_location_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, index=True, null=True)
    commodity = TextField(null=True, index=True)
    service_provider_id = UUIDField(index=True, null=True)
    importer_exporter_id = UUIDField(null=True)
    importer_exporters_count = IntegerField(null=True)
    line_items = BinaryJSONField(null = True)
    is_best_price = BooleanField(null=True)
    is_line_items_error_messages_present = BooleanField(null=True)
    is_line_items_info_messages_present = BooleanField(null=True)
    line_items_error_messages = BinaryJSONField(null = True)
    line_items_info_messages = BinaryJSONField(null= True)
    truck_type = TextField(null=True,index = True)
    truck_body_type = TextField(index=True, null=True)
    trip_type = CharField(index=True, null = True)
    minimum_chargeable_weight = FloatField(index=True, null=True)
    transit_time = IntegerField(index=True, null = True)
    unit = CharField(index=True, null=True)
    trucks_count = IntegerField(null=True)
    rate_not_available_entry = BooleanField(constraints=[SQL("DEFAULT false")], null=True, index=True)
    validity_start = DateTimeField(default=datetime.datetime.now, null=True)
    validity_end = DateTimeField(default = datetime.datetime.now() + datetime.timedelta(15), null=True)
    detention_free_time = CharField(index=True, null = True)
    importer_exporter = BinaryJSONField(null=True)
    service_provider = BinaryJSONField(null=True)
    origin_location = BinaryJSONField(index=True, null=True)
    destination_location = BinaryJSONField(index=True, null=True)
    created_at = DateTimeField(default=datetime.datetime.now, index=True)
    updated_at = DateTimeField(default=datetime.datetime.now, index=True)
    mode = CharField(default = 'manual', index=True, null = True)
    accuracy = FloatField(default = 100, null = True)
    sourced_by_id = UUIDField(null=True, index=True)
    procured_by_id = UUIDField(null=True, index=True)
    sourced_by = BinaryJSONField(null=True)
    procured_by = BinaryJSONField(null=True)
    rate_type = CharField(default='market_place', choices = RATE_TYPES, index=True)
    tags = BinaryJSONField(null=True)
    init_key = TextField(index=True, null=True)
    
    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(FtlFreightRate, self).save(*args, **kwargs)

    class Meta:
        table_name = 'ftl_freight_rates'

    def set_locations(self):
        ids = [str(self.origin_location_id), str(self.destination_location_id)]
        locations_response = maps.list_locations({'filters':{"id": ids}})
        locations = []
        if 'list' in locations_response:
            locations = locations_response["list"]
        for location in locations:
            if str(location['id']) == str(self.origin_location_id):
                self.origin_location = self.get_required_location_data(location)
            elif str(location['id']) == str(self.destination_location_id):
                self.destination_location = self.get_required_location_data(location)
        self.set_origin_location_ids()
        self.set_origin_location_type()
        self.set_destination_location_ids()
        self.set_destination_location_type()
        self.set_origin_destination_location_type()

    def get_required_location_data(self, location):
        loc_data = {
          "id": location["id"],
          "name": location["name"],
          "is_icd": location["is_icd"],
          "type": location["type"],
          "cluster_id": location["cluster_id"],
          "city_id": location["city_id"],
          "country_id": location["country_id"],
          "country_code": location["country_code"]
        }
        return loc_data

    def set_origin_location_ids(self):
        self.origin_cluster_id = self.origin_location.get('cluster_id')
        self.origin_city_id = self.origin_location.get('city_id')
        self.origin_country_id = self.origin_location.get('country_id')
        if re.match(r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$', str(self.origin_cluster_id)):
            self.origin_location_ids = [uuid.UUID(str(self.origin_location_id)), uuid.UUID(str(self.origin_cluster_id)),uuid.UUID(str(self.origin_city_id)),uuid.UUID(str(self.origin_country_id))]
        else:
            self.origin_location_ids = [uuid.UUID(str(self.origin_location_id)),uuid.UUID(str(self.origin_city_id)),uuid.UUID(str(self.origin_country_id))]

    def set_origin_location_type(self):
        self.origin_location_type = self.origin_location.get('type')

    def set_destination_location_ids(self):
        self.destination_cluster_id = self.destination_location.get('cluster_id')
        self.destination_city_id = self.destination_location.get('city_id')
        self.destination_country_id = self.destination_location.get('country_id')
        if re.match(r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$', str(self.destination_cluster_id)):
            self.destination_location_ids = [uuid.UUID(str(self.destination_location_id)), uuid.UUID(str(self.destination_cluster_id)),uuid.UUID(str(self.destination_city_id)),uuid.UUID(str(self.destination_country_id))]
        else:
            self.destination_location_ids = [uuid.UUID(str(self.destination_location_id)), uuid.UUID(str(self.destination_city_id)),uuid.UUID(str(self.destination_country_id))]        
    
    def set_destination_location_type(self):
        self.destination_location_type = self.destination_location.get('type')
    
    def set_origin_destination_location_type(self):
        self.origin_destination_location_type = ':'.join([str(self.origin_location_type),str(self.destination_location_type)])
    
    def validate_validities(self, validity_start, validity_end):
        
        if not validity_start:
            raise HTTPException(status_code=400, detail="validity_start is invalid")
        
        if not validity_end:
            raise HTTPException(status_code=400, detail="validity_end is invalid")
        
        if validity_end < validity_start:
            raise HTTPException(status_code=400, detail="validity_end can not be lesser than validity_start")
        
    def validate_duplicate_line_items(self):
        self.line_items = self.line_items or []
        if len(set(map(lambda t: str(t['code']).upper(), self.line_items))) != len(self.line_items):
            raise HTTPException(status_code=500, detail="Contains Duplicates")
        
    def validate_truck_body_type(self):
        if self.truck_body_type not in BODY_TYPE:
            raise HTTPException(status_code=400, detail="Invalid truck_body_type")
    
    def validate_trip_type(self):
        if self.trip_type not in TRIP_TYPES:
            raise HTTPException(status_code=400, detail="Invalid trip_type")
        
    def validate_origin_destination_locations(self):
        if self.origin_location_id == self.destination_location_id and self.origin_location_type == 'pincode':
            raise HTTPException(status_code=400, detail="origin_location and destination_location can not be same")
        
    def validate_minimum_chargeable_weight(self):
        if self.unit == 'per_ton' and not self.minimum_chargeable_weight:
            raise HTTPException(status_code=400, detail="minimum_chargeable_weight is required")
        
    def validate_unit(self):
        if self.unit and self.unit not in VALID_UNITS:
            raise HTTPException(status_code=400, detail="Invalid unit")
        
    def validate_transit_time(self):
        if self.transit_time <=0:
            raise HTTPException(status_code=400, detail="Invalid transit_time")
        
    def validate_detention_free_time(self):
        if self.detention_free_time < 0:
            raise HTTPException(status_code=400, detail="Invalid detention_free_time")
        
    def validate_commoditiy(self):
        if self.commodity not in COMMODITIES:
            raise HTTPException(status_code=400, detail="Invalid commodity")
    
    