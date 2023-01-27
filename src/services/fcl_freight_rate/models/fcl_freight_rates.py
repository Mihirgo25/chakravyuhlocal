from peewee import * 
import datetime
from database.db_session import db
from playhouse.postgres_ext import *
from pydantic import BaseModel as pydantic_base_model
from peewee import fn
from typing import Set, Union
from fastapi import FastAPI, HTTPException
import yaml
from services.fcl_freight_rate.models.fcl_freight_rate_line_item import lineItem
from services.fcl_freight_rate.models.fcl_freight_rate_slab import slab
from services.fcl_freight_rate.models.fcl_freight_rate_line_item import lineItem
from services.fcl_freight_rate.models.fcl_freight_rate_validity import FclFreightRateValidity


def to_dict(obj):
    return json.loads(json.dumps(obj, default=lambda o: o.__dict__))

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = db
        
class FclFreightRate(BaseModel):
    commodity = CharField(null=True)
    container_size = CharField(null=True)
    container_type = CharField(null=True)
    containers_count = IntegerField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    destination_continent_id = UUIDField(index=True, null=True)
    destination_country_id = UUIDField(index=True, null=True)
    destination_demurrage_id = UUIDField(index=True, null=True)
    destination_detention_id = UUIDField(index=True, null=True)
    destination_local = BinaryJSONField(null=True)
    destination_local_id = UUIDField(index=True, null=True)
    destination_local_line_items_error_messages = BinaryJSONField(constraints=[SQL("DEFAULT '{}'::jsonb")], null=True)
    destination_local_line_items_info_messages = BinaryJSONField(constraints=[SQL("DEFAULT '{}'::jsonb")], null=True)
    destination_location_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, index=True, null=True)
    destination_main_port_id = UUIDField(null=True)
    destination_plugin_id = UUIDField(index=True, null=True)
    destination_port_id = UUIDField(index=True, null=True)
    destination_trade_id = UUIDField(index=True, null=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    importer_exporter_id = UUIDField(null=True)
    importer_exporters_count = IntegerField(null=True)
    is_best_price = BooleanField(null=True)
    is_destination_demurrage_slabs_missing = BooleanField(index=True, null=True)
    is_destination_detention_slabs_missing = BooleanField(index=True, null=True)
    is_destination_local_line_items_error_messages_present = BooleanField(index=True, null=True)
    is_destination_local_line_items_info_messages_present = BooleanField(index=True, null=True)
    is_destination_plugin_slabs_missing = BooleanField(index=True, null=True)
    is_origin_demurrage_slabs_missing = BooleanField(index=True, null=True)
    is_origin_detention_slabs_missing = BooleanField(index=True, null=True)
    is_origin_local_line_items_error_messages_present = BooleanField(index=True, null=True)
    is_origin_local_line_items_info_messages_present = BooleanField(index=True, null=True)
    is_origin_plugin_slabs_missing = BooleanField(index=True, null=True)
    is_weight_limit_slabs_missing = BooleanField(null=True)
    last_rate_available_date = DateField(null=True)
    omp_dmp_sl_sp = CharField(null=True)
    origin_continent_id = UUIDField(index=True, null=True)
    origin_country_id = UUIDField(index=True, null=True)
    origin_detention_id = UUIDField(index=True, null=True)
    origin_local = BinaryJSONField(null=True)
    origin_local_id = UUIDField(index=True, null=True)
    origin_local_line_items_error_messages = BinaryJSONField(constraints=[SQL("DEFAULT '{}'::jsonb")], null=True)
    origin_local_line_items_info_messages = BinaryJSONField(constraints=[SQL("DEFAULT '{}'::jsonb")], null=True)
    origin_location_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, index=True, null=True)
    origin_main_port_id = UUIDField(null=True)
    origin_plugin_id = UUIDField(index=True, null=True)
    origin_port_id = UUIDField(null=True)
    origin_trade_id = UUIDField(index=True, null=True)
    priority_score = IntegerField(null=True)
    priority_score_updated_at = DateTimeField(null=True)
    rate_not_available_entry = BooleanField(constraints=[SQL("DEFAULT false")], null=True)
    service_provider_id = UUIDField(index=True, null=True)
    shipping_line_id = UUIDField(index=True, null=True)
    updated_at = DateTimeField(default=datetime.datetime.now)
    validities = BinaryJSONField(default = [], null=True)
    weight_limit = BinaryJSONField(null=True)
    weight_limit_id = UUIDField(index=True, null=True)

    class Meta:
        table_name = 'fcl_freight_rates'
        indexes = (
            (('container_size', 'container_type', 'commodity'), False),
            (('container_type', 'commodity'), False),
            (('importer_exporter_id', 'service_provider_id'), False),
            (('origin_port_id', 'destination_port_id', 'container_size', 'container_type', 'commodity', 'importer_exporter_id', 'rate_not_available_entry', 'last_rate_available_date', 'omp_dmp_sl_sp'), False),
            (('origin_port_id', 'destination_port_id', 'container_size', 'container_type', 'commodity', 'shipping_line_id', 'service_provider_id'), True),
            (('origin_port_id', 'destination_port_id', 'container_size', 'container_type', 'commodity', 'shipping_line_id', 'service_provider_id', 'importer_exporter_id'), True),
            (('origin_port_id', 'destination_port_id', 'destination_main_port_id', 'container_size', 'container_type', 'commodity', 'shipping_line_id', 'service_provider_id'), True),
            (('origin_port_id', 'destination_port_id', 'destination_main_port_id', 'container_size', 'container_type', 'commodity', 'shipping_line_id', 'service_provider_id', 'importer_exporter_id'), True),
            (('origin_port_id', 'origin_main_port_id', 'destination_port_id', 'container_size', 'container_type', 'commodity', 'shipping_line_id', 'service_provider_id'), True),
            (('origin_port_id', 'origin_main_port_id', 'destination_port_id', 'container_size', 'container_type', 'commodity', 'shipping_line_id', 'service_provider_id', 'importer_exporter_id'), True),
            (('origin_port_id', 'origin_main_port_id', 'destination_port_id', 'destination_main_port_id', 'container_size', 'container_type', 'commodity', 'shipping_line_id', 'service_provider_id'), True),
            (('origin_port_id', 'origin_main_port_id', 'destination_port_id', 'destination_main_port_id', 'container_size', 'container_type', 'commodity', 'shipping_line_id', 'service_provider_id', 'importer_exporter_id'), True),
            (('priority_score', 'id', 'service_provider_id'), False),
            (('priority_score', 'service_provider_id'), False),
            (('priority_score', 'service_provider_id', 'importer_exporter_id'), False),
            (('priority_score', 'service_provider_id', 'is_best_price'), False),
            (('priority_score', 'service_provider_id', 'last_rate_available_date'), False),
            (('priority_score', 'service_provider_id', 'rate_not_available_entry'), False),
            (('priority_score', 'service_provider_id', 'shipping_line_id', 'is_best_price'), False),
            (('priority_score', 'service_provider_id', 'shipping_line_id', 'rate_not_available_entry'), False),
            (('service_provider_id', 'id'), False),
            (('service_provider_id', 'shipping_line_id', 'container_size', 'container_type', 'commodity'), False),
            (('updated_at', 'id', 'service_provider_id'), False),
            (('updated_at', 'service_provider_id'), False),
        )

    def validate_validity_object(self, validity_start, validity_end):
      if not validity_start:
        raise HTTPException(status_code=499, detail="validity_start is invalid")

      if not validity_end:
        raise HTTPException(status_code=499, detail="validity_end is invalid")

      if validity_end > (datetime.datetime.now().date() + datetime.timedelta(days=60)):
        raise HTTPException(status_code=499, detail="validity_end can not be greater than 60 days from current date")

      if validity_start < (datetime.datetime.now().date() - datetime.timedelta(days=15)):
        raise HTTPException(status_code=499, detail="validity_start can not be less than 15 days from current date")

      if validity_end < validity_start:
        raise HTTPException(status_code=499, detail="validity_end can not be lesser than validity_start")

    def validate_line_items(self, line_items):
      codes = [item["code"] for item in line_items]
      if len(set(codes)) != len(codes):
        raise HTTPException(status_code=499, detail="line_items contains duplicates")

      with open('/Users/uditpal/ocean-rms/src/charges/fcl_freight_charges.yml', 'r') as file:
        fcl_freight_charges_dict = yaml.safe_load(file)

      invalid_line_items = [code for code in codes if code not in fcl_freight_charges_dict]

      
      if invalid_line_items:
          raise HTTPException(status_code=499, detail="line_items {} are invalid".format(", ".join(invalid_line_items)))

      #an api call to ListMoneyCurrencies

      mandatory_codes = []

      for code, config in fcl_freight_charges_dict.items():
        try:
          condition_value = eval(config["condition"])
        except:
          condition_value = False

        if not condition_value:
          continue

        if "mandatory" in config["tags"]:
          mandatory_codes.append(str(code))
        
      if len([code for code in mandatory_codes if code not in codes]) > 0:
          raise HTTPException(status_code=499, detail="line_items does not contain all mandatory_codes {}".format(", ".join([code for code in mandatory_codes if code not in codes])))

    def set_validities(self, validity_start, validity_end, line_items, schedule_type, deleted, payment_term):
        new_validities = []

        if not deleted:
            currency = [item for item in line_items if item["code"] == "BAS"][0]["currency"]
            price = 100
            # price = sum([GetMoneyExchange.run(price=item["price"], from_currency=item["currency"], to_currency=currency)["price"] for item in line_items])
            new_validity_object = {
                "validity_start": validity_start,
                "validity_end": validity_end,
                "line_items": line_items,
                "price": price,
                "currency": currency,
                "schedule_type": schedule_type,
                "payment_term": payment_term,
                "id": str(uuid.uuid4()),
                "likes_count": 0,
                "dislikes_count": 0
            }
            new_validities = [FclFreightRateValidity(**new_validity_object)]

        # print(self.validities)
        for validity_object in self.validities:
            validity_object_validity_start = datetime.datetime.strptime(validity_object['validity_start'], "%Y-%m-%d").date()
            validity_object_validity_end = datetime.datetime.strptime(validity_object['validity_end'], "%Y-%m-%d").date()
            if (validity_object['schedule_type'] not in [None, schedule_type] and not deleted):
                new_validities.append(validity_object)
                continue
            if (validity_object['payment_term'] not in [None, payment_term] and not deleted):
                new_validities.append(validity_object)
                continue
            if validity_object_validity_start > validity_end:
                new_validities.append(validity_object)
                continue
            if validity_object_validity_end < validity_start:
                new_validities.append(validity_object)
                continue
            if validity_object_validity_start >= validity_start and validity_object_validity_end <= validity_end:
                continue
            if validity_object_validity_start < validity_start and validity_object_validity_end <= validity_end:
                validity_object_validity_end = validity_start - datetime.timedelta(days=1)
                new_validities.append(validity_object)
                continue
            if validity_object_validity_start >= validity_start and validity_object_validity_end > validity_end:
                validity_object_validity_start = validity_end + datetime.timedelta(days=1)
                new_validities.append(validity_object)
                continue
            if validity_object_validity_start < validity_start and validity_object_validity_end > validity_end:
                new_validities.append(FclFreightRateValidity(validity_object['json']().update({"validity_end": validity_start - datetime.timedelta(days=1)})))
                new_validities.append(FclFreightRateValidity(validity_object['json']().update({"validity_start": validity_end + datetime.timedelta(days=1)})))
                continue

        new_validities = [validity for validity in new_validities if validity.validity_end >= datetime.datetime.now().date()]
        new_validities = sorted(new_validities, key=lambda validity: validity.validity_start)

        for new_validity in new_validities:
          new_validity.line_items = [dict(line_item) for line_item in new_validity.line_items]
          new_validity.validity_start = new_validity.validity_start.isoformat()
          new_validity.validity_end = new_validity.validity_end.isoformat()
        
        self.validities = [dict(new_validity) for new_validity in new_validities]

    def get_platform_price(self, validity_start, validity_end, price, currency):
      freight_rates = FclFreightRate.select().where(
            (FclFreightRate.origin_port_id == self.origin_port_id) &
            (FclFreightRate.origin_main_port_id == self.origin_main_port_id) &
            (FclFreightRate.destination_port_id == self.destination_port_id) &
            (FclFreightRate.destination_main_port_id == self.destination_main_port_id) &
            (FclFreightRate.container_size == self.container_size) &
            (FclFreightRate.container_type == self.container_type) &
            (FclFreightRate.commodity == self.commodity) &
            (FclFreightRate.shipping_line_id == self.shipping_line_id)
            ).where(FclFreightRate.importer_exporter_id.in_([None, self.importer_exporter_id])).where(FclFreightRate.service_provider_id.not_in([self.service_provider_id]))

      result = price

      validities = []
      if freight_rates:
        for freight_rate in freight_rates:
          for t in freight_rate.validities:
            if (validity_start <= t.validity_end) & (validity_end >= t.validity_start):
              validities.append(t)

        #   for t in validities:
            # result = min(result, GetMoneyExchange.run(price=t.price, from_currency=t.currency, to_currency=currency)["price"])
      
      return result
    
    def set_platform_prices(self):
      for validity_object in self.validities:
        validity_object['platform_price'] = self.get_platform_price(validity_object['validity_start'], validity_object['validity_end'], validity_object['price'], validity_object['currency'])

    def set_is_best_price(self):
      if(self.validities.count == 0):
        self.is_best_price = None
      else:
        temp = []
        for t in self.validities:
          if(t['platform_price'] < t['price']):
            temp.append(t)
        
        self.is_best_price = len(temp)<=0

    def set_last_rate_available_date(self):
      if(self.validities):
        self.last_rate_available_date = self.validities[-1]['validity_end']
      else:
        self.last_rate_available_date = None

    #   print(self.last_rate_available_date)
    
    def delete_rate_not_available_entry(self):
      FclFreightRate.delete().where(
            (FclFreightRate.origin_port_id == self.origin_port_id) &
            (FclFreightRate.destination_port_id == self.destination_port_id) &
            (FclFreightRate.container_size == self.container_size) &
            (FclFreightRate.container_type == self.container_type) &
            (FclFreightRate.commodity == self.commodity) &
            (FclFreightRate.service_provider_id == self.service_provider_id) &
            (FclFreightRate.rate_not_available_entry == True)
      )

# class slab(pydantic_base_model):
#   lower_limit: float
#   upper_limit: float
#   price: float
#   currency: str

# class lineItem(pydantic_base_model):
#   location_id: str = None  # different line_items
#   code: str
#   unit: str
#   price: float
#   currency: str
#   remarks: list[str] = None
#   slabs: list[slab] = None

class freeDay(pydantic_base_model):
  free_limit: float
  slabs: list[slab] = None
  remarks: list[str] = None

class originLocal(pydantic_base_model):
  line_items: list[lineItem]
  detention: freeDay
  demurrage: freeDay
  plugin: freeDay

class destinationLocal(pydantic_base_model):
  line_items: list[lineItem]
  detention: freeDay
  demurrage: freeDay
  plugin: freeDay

class standardLineItem(pydantic_base_model):
  code: str
  unit: str
  price: float
  currency: str
  remarks: list[str] = []
  slabs: list[slab] = None

class postFclFreightRate(pydantic_base_model):
  origin_main_port_id: str = None
  origin_port_id: str
  destination_port_id: str
  destination_main_port_id: str = None
  container_size: str
  container_type: str
  commodity: str
  shipping_line_id: str
  service_provider_id: str
  importer_exporter_id: str = None
  validity_start: datetime.date
  validity_end: datetime.date
  schedule_type: str = 'transhipment'
  fcl_freight_rate_request_id: str = None
  payment_term: str = 'prepaid'
  line_items: list[standardLineItem]
  weight_limit: freeDay = None
  origin_local: originLocal = None
  destination_local: destinationLocal = None