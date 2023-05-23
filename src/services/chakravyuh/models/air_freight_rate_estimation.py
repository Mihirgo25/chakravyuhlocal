from peewee import *
from database.db_session import db
import datetime
from playhouse.postgres_ext import *
from micro_services.client import common, maps
from services.chakravyuh.models.fcl_freight_rate_estimation_audit import FclFreightRateEstimationAudit

class BaseModel(Model):
    class Meta:
        database = db

class AirFreightRateEstimation(BaseModel):
    id = BigAutoField(primary_key=True)
    origin_location_id = UUIDField(index=True, null=False)
    origin_location_type = CharField(null=False, index=True)
    destination_location_id = UUIDField(index=True, null=False)
    destination_location_type = CharField(null=False, index=True)
    airline_id = UUIDField(null=True, index=True)
    commodity = CharField(null=False)
    operation_type = TextField(null=False)
    line_items = BinaryJSONField(default=[])
    stacking_type = TextField(null=True)
    shipment_type = TextField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    status = CharField(default="active", null=False)
    origin_location = BinaryJSONField(null=True)
    destination_location = BinaryJSONField(null=True)
    airline = BinaryJSONField(null=True)

    class Meta:
        table_name = "air_freight_rate_estimations"

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(AirFreightRateEstimation, self).save(*args, **kwargs)
    
    def set_attribute_objects(self):
        from database.rails_db import get_shipping_line
        location_ids = [str(self.origin_location_id), str(self.destination_location_id)]

        locations_response = maps.list_locations({ 'filters': { 'id': location_ids }})

        if 'list' in locations_response:
            locations_list = locations_response['list']
            for location in locations_list:
                if location['id'] == str(self.origin_location_id):
                    self.origin_location = location
                if location['id'] == str(self.destination_location_id):
                    self.destination_location = location
        if self.airline_id:
            airline_list = get_shipping_line(str(self.airline_id))

            if airline_list:
                self.airline = airline_list[0]
        
        self.save()



    
    def set_line_items(self, line_items):
        new_line_items = []
        for req_item in line_items:
            for item in self.line_items:
                if item['code'] == req_item['code']:
                    std_dev_old = item['stand_dev']
                    mean_old = item['mean']
                    size_old = item['size']
                    size_new = size_old + 1
                    price_new = req_item['price']
                    if req_item['currency'] != item['currency']:
                        price_new = common.get_money_exchange_for_fcl({"price": req_item['price'], "from_currency": req_item['currency'], "to_currency": item['currency'] })['price']
                    mean_new = (mean_old * size_old + price_new) / size_new    
                    std_dev_new = ((size_new - 1) * std_dev_old ** 2 + (price_new - mean_old) ** 2 / size_new) ** 0.5
                    item['price'] = price_new
                    item['lower_limit'] = mean_new - 2 * std_dev_new
                    item['upper_limit'] = mean_new + 2 * std_dev_new
                    item['mean'] = mean_new
                    item['stand_dev'] = std_dev_new
                    item['size'] = size_new
                    new_line_items.append(item)
                    break
                else:
                    item['lower_limit'] = item['price']
                    item['upper_limit'] = item['price']
                    item['mean'] = item['price']
                    item['stand_dev'] = 0
                    item['size'] = 1
                    new_line_items.append(item)
                    
    def create_audit(self, param):
        audit = FclFreightRateEstimationAudit.create(**param)
        return audit