from peewee import *
import datetime
from datetime import date
from database.db_session import db
from playhouse.postgres_ext import *
from pydantic import BaseModel as pydantic_base_model
from peewee import fn
from typing import Set, Union
from fastapi import FastAPI, HTTPException
import yaml
from params import LineItem
from services.fcl_freight_rate.models.fcl_freight_rate_locals import FclFreightRateLocal
from configs.fcl_freight_rate_constants import *
from schema import Schema, Optional, Or, SchemaError
from configs.defintions import FCL_FREIGHT_CHARGES
from rails_client import client
from params import FreeDay
from celery import current_app, shared_task


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
    destination_local_id = ForeignKeyField(FclFreightRateLocal, index=True, null=True)
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
    origin_local_id = ForeignKeyField(FclFreightRateLocal, index=True, null=True)
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
    source = CharField(default = 'manual', null = True)
    accuracy = FloatField(default = 100, null = True)
    cogo_entity_id = UUIDField(index=True, null=True)
    origin_port: dict = None
    destination_port: dict = None
    origin_main_port: dict = None
    destination_main_port: dict = None
    shipping_line: dict = None

    class Meta:
        table_name = 'fcl_freight_rates'
        indexes = (
            (('container_size', 'container_type', 'commodity'), False),
            (('container_type', 'commodity'), False),
            (('importer_exporter_id', 'service_provider_id'), False),
            (('origin_port_id', 'destination_port_id', 'container_size', 'container_type', 'commodity', 'importer_exporter_id', 'rate_not_available_entry', 'last_rate_available_date', 'omp_dmp_sl_sp'), False),
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

    def set_locations(self):
      obj = {"filters" : {"id": [str(self.origin_port_id), str(self.destination_port_id), str(self.origin_main_port_id), str(self.destination_main_port_id)]}}
      locations = client.ruby.list_locations(obj)['list']

      for location in locations:
        if str(self.origin_port_id) == location['id']:
          self.origin_port = location
        if str(self.destination_port_id) == location['id']:
          self.destination_port = location
        if str(self.origin_main_port_id) == location['id']:
          self.origin_main_port = location
        if str(self.destination_main_port_id) == location['id']:
          self.destination_main_port = location

    def set_origin_location_ids(self):
      self.origin_country_id = self.origin_port.get('country_id')
      self.origin_continent_id = self.origin_port.get('continent_id')
      self.origin_trade_id = self.origin_port.get('trade_id')
      self.origin_location_ids = [uuid.UUID(str(self.origin_port_id)),uuid.UUID(str(self.origin_country_id)),uuid.UUID(str(self.origin_trade_id)),uuid.UUID(str(self.origin_continent_id))]

    def set_destination_location_ids(self):
      self.destination_country_id = self.destination_port.get('country_id')
      self.destination_continent_id = self.destination_port.get('continent_id')
      self.destination_trade_id = self.destination_port.get('trade_id')
      self.destination_location_ids = [uuid.UUID(str(self.destination_port_id)),uuid.UUID(str(self.destination_country_id)),uuid.UUID(str(self.destination_trade_id)),uuid.UUID(str(self.destination_continent_id))]

    def validate_origin_main_port_id(self):
      if self.origin_port and self.origin_port['is_icd'] == False:
        if not self.origin_main_port_id:
          return True
        return False

    def validate_destination_main_port_id(self):
      if self.destination_port and self.destination_port['is_icd'] == False:
        if not self.destination_main_port_id:
          return True
        return False

    def set_shipping_line(self):
      if not self.rate_not_available_entry:
        shipping_line = client.ruby.list_operators({'filters':{'id': str(self.shipping_line_id)}})['list'][0]
        if shipping_line:
          self.shipping_line = shipping_line
          return True
        return False

    def validate_service_provider(self):
      service_provider = client.ruby.list_organizations({'filters':{'id': str(self.service_provider_id)}})['list'][0]
      if service_provider.get('account_type') == 'service_provider':
        self.service_provider = service_provider
        return True
      return False

    def validate_importer_exporter(self):
      importer_exporter = client.ruby.list_organizations({'filters':{'id': str(self.importer_exporter_id)}})['list'][0]
      if importer_exporter:
        if importer_exporter.get('account_type') == 'importer_exporter':
          self.importer_exporter = importer_exporter
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

    def validate_commodity(self):
      if self.container_type and self.commodity in FREIGHT_CONTAINER_COMMODITY_MAPPINGS[f"{self.container_type}"]:
        return True
      return False

    def valid_uniqueness(self):
      freight_cnt = FclFreightRate.select().where(
        FclFreightRate.origin_port_id == self.origin_port_id,
        FclFreightRate.origin_main_port_id == self.origin_main_port_id,
        FclFreightRate.destination_port_id == self.destination_port_id,
        FclFreightRate.destination_main_port_id == self.destination_main_port_id,
        FclFreightRate.container_size == self.container_size,
        FclFreightRate.container_type == self.container_type,
        FclFreightRate.commodity == self.commodity,
        FclFreightRate.shipping_line_id == self.shipping_line_id,
        FclFreightRate.service_provider_id == self.service_provider_id,
        FclFreightRate.importer_exporter_id == self.importer_exporter_id
      ).count()

      if self.id and freight_cnt==1:
        return True
      if not self.id and freight_cnt==0:
        return True

      return False

    def set_omp_dmp_sl_sp(self):
      self.omp_dmp_sl_sp = ":".join([str(self.origin_main_port_id), str(self.destination_main_port_id), str(self.shipping_line_id), str(self.service_provider_id)])

    def update_special_attributes(self):
      self.update_origin_local_line_item_messages()
      self.update_destination_local_line_item_messages()
      self.update_origin_free_days_special_attributes()
      self.update_destination_free_days_special_attributes()
      self.update_weight_limit_special_attributes()

    def update_origin_local_line_item_messages(self):
      response = {}

      if self.origin_local:
        response = dict(self.local_data_get_line_item_messages())
      self.update(
      origin_local_line_items_error_messages = response.get('line_items_error_messages'),
      is_origin_local_line_items_error_messages_present = response.get('is_line_items_error_messages_present'),
      origin_local_line_items_info_messages = response.get('line_items_info_messages'),
      is_origin_local_line_items_info_messages_present = response.get('is_line_items_info_messages_present'))

    def update_destination_local_line_item_messages(self):
      response = {}

      if self.destination_local:
        response = dict(self.local_data_get_line_item_messages())
      self.update(
      destination_local_line_items_error_messages = response.get('line_items_error_messages'),
      is_destination_local_line_items_error_messages_present = response.get('is_line_items_error_messages_present'),
      destination_local_line_items_info_messages = response.get('line_items_info_messages'),
      is_destination_local_line_items_info_messages_present = response.get('is_line_items_info_messages_present'))

    def update_origin_free_days_special_attributes(self):
      self.update(
        is_origin_detention_slabs_missing = (len(self.origin_local.get('detention',{}).get('slabs',{})) == 0),
        is_origin_demurrage_slabs_missing = (len(self.origin_local.get('demurrage',{}).get('slabs',{})) == 0),
        is_origin_plugin_slabs_missing = (len(self.origin_local.get('plugin',{}).get('slabs',{})) == 0)
      )

    def update_destination_free_days_special_attributes(self):
      self.update(
        is_destination_detention_slabs_missing = (len(self.destination_local.get('detention',{}).get('slabs',{})) == 0),
        is_destination_demurrage_slabs_missing = (len(self.destination_local.get('demurrage',{}).get('slabs',{})) == 0),
        is_destination_plugin_slabs_missing = (len(self.destination_local.get('plugin',{}).get('slabs',{})) == 0)
      )

    def update_weight_limit_special_attributes(self):
      self.update(is_weight_limit_slabs_missing = (len(self.weight_limit.get('slabs',{})) == 0))

    def validate_origin_local(self):
      if 'origin_local' in self.changes and self.origin_local:
        self.origin_local.validate_duplicate_charge_codes() #call to local store model function
        self.origin_local.validate_invalid_charge_codes(self.possible_origin_local_charge_codes) #call to local store model function

    def validate_destination_local(self):
      if 'destination_local' in self.changes and self.destination_local:
        self.destination_local.validate_duplicate_charge_codes #call to local function
        self.destination_local.validate_invalid_charge_codes(self.possible_destination_local_charge_codes) #call to local function

    # def set_origin_main_port(self):
    #   if self.origin_port and self.origin_port['icd'] == True and not self.rate_not_available_entry:
    #     "set origin_main_port"

    # def set_destination_main_port(self):
    #   if self.destination_port and self.destination_port['icd'] == True and not self.rate_not_available_entry:
    #     "set destination_main_port"


    def validate_validity_object(self, validity_start, validity_end):
      if not validity_start:
        raise HTTPException(status_code=499, detail="validity_start is invalid")

      if not validity_end:
        raise HTTPException(status_code=499, detail="validity_end is invalid")

      if validity_end.date() > (datetime.datetime.now().date() + datetime.timedelta(days=60)):
        raise HTTPException(status_code=499, detail="validity_end can not be greater than 60 days from current date")

      if validity_start.date() < (datetime.datetime.now().date() - datetime.timedelta(days=15)):
        raise HTTPException(status_code=499, detail="validity_start can not be less than 15 days from current date")

      if validity_end < validity_start:
        raise HTTPException(status_code=499, detail="validity_end can not be lesser than validity_start")

    def validate_line_items(self, line_items):
      codes = [item['code'] for item in line_items]

      if len(set(codes)) != len(codes):
        raise HTTPException(status_code=499, detail="line_items contains duplicates")

      #should we put self in condition in fcl_freight_charges yml
      with open(FCL_FREIGHT_CHARGES, 'r') as file:
        fcl_freight_charges_dict = yaml.safe_load(file)

      invalid_line_items = [code for code in codes if code not in fcl_freight_charges_dict.keys()]
      
      if invalid_line_items:
          raise HTTPException(status_code=499, detail="line_items {} are invalid".format(", ".join(invalid_line_items)))

      # #an api call to ListMoneyCurrencies

      mandatory_codes = []

      origin_port = self.origin_port
      destination_port = self.destination_port
      shipping_line = self.shipping_line
      commodity = self.commodity
      container_type = self.container_type
      container_size = self.container_size

      for code, config in fcl_freight_charges_dict.items():
        try:
          condition_value = eval(str(config["condition"]))
        except:
          condition_value = False

        if not condition_value:
          continue

        if "mandatory" in config["tags"]:
          mandatory_codes.append(str(code))

      if len([code for code in mandatory_codes if code not in codes]) > 0:
          raise HTTPException(status_code=499, detail="line_items does not contain all mandatory_codes {}".format(", ".join([code for code in mandatory_codes if code not in codes])))

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

          for t in validities:
            price = []
            new_price =  client.ruby.get_money_exchange_for_fcl({'price': t.price, 'from_currency': t.currency, 'to_currency':currency})['list']['price']
            price.append(new_price)
            freight_rate_min_price = min(price)

          if freight_rate_min_price < result & freight_rate_min_price is not None:      
            result = freight_rate_min_price    
      
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

    def set_validities(self, validity_start, validity_end, line_items, schedule_type, deleted, payment_term):
        new_validities = []

        if not deleted:
            currency = [item for item in line_items if item["code"] == "BAS"][0]["currency"]
            price = float(100)
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

        for validity_object in self.validities:
            validity_object_validity_start = datetime.datetime.strptime(validity_object['validity_start'], "%Y-%m-%d").date()
            validity_object_validity_end = datetime.datetime.strptime(validity_object['validity_end'], "%Y-%m-%d").date()
            validity_start = validity_start
            validity_end = validity_end
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
        
        self.validities = [vars(new_validity) for new_validity in new_validities]

    def delete_rate_not_available_entry(self):
      FclFreightRate.delete().where(
            FclFreightRate.origin_port_id == self.origin_port_id,
            FclFreightRate.destination_port_id == self.destination_port_id,
            FclFreightRate.container_size == self.container_size,
            FclFreightRate.container_type == self.container_type,
            FclFreightRate.commodity == self.commodity,
            FclFreightRate.service_provider_id == self.service_provider_id,
            FclFreightRate.rate_not_available_entry == True
      ).execute()

    def validate_before_save(self):   # check correctly
      #put schema validates in try catch and then raise custom error
      schema_weight_limit = Schema({'free_limit': float, Optional('slabs'): list, Optional('remarks'): list})
     
      if self.weight_limit:
        # if 'slabs' in self.weight_limit:
        #   for slab in self.weight_limit['slabs']:
        #     if 'price' in slab:
        #         slab['price'] = float(slab['price'])
        schema_weight_limit.validate(self.weight_limit)

      self.weight_limit['slabs'] = sorted(self.weight_limit['slabs'], key=lambda x: x['lower_limit'])

      if self.weight_limit['slabs'] and self.weight_limit['free_limit']!=0 and (self.weight_limit['free_limit'] >= self.weight_limit['slabs'][0]['lower_limit']):
        raise HTTPException(status_code=499, detail="slabs lower limit should be greater than free limit")

      for index, weight_limit_slab in enumerate(self.weight_limit['slabs']):
        if (weight_limit_slab['upper_limit'] <= weight_limit_slab['lower_limit']) or (index != 0 and weight_limit_slab['lower_limit'] <= self.weight_limit['slabs'][index - 1]['upper_limit']):
          raise HTTPException(status_code=499, detail="slabs are not valid")

      schema_validity = Schema({'validity_start': str, 'validity_end': str, 'price': float, 'currency': str, 'platform_price': float, Optional('remarks'): list, Optional('line_items'): list, Optional('schedule_type', lambda s: s in ('direct', 'transhipment')): str, Optional('payment_term', lambda s: s in ('prepaid', 'collect')): str, Optional('id'): str, Optional('likes_count'): int, Optional('dislikes_count'): int})

      for validity in self.validities:
        validity['id'] = validity['__data__']['id']
        validity.pop('__data__', None)
        validity.pop('__rel__', None)
        validity.pop('_dirty', None)

        schema_validity.validate(validity)

      schema_local_data = Schema({Optional('line_items'): list, Optional('detention'): dict, Optional('demurrage'): dict, Optional('plugin'): dict})

      if self.origin_local:
        schema_local_data.validate(self.origin_local)
      if self.destination_local:
        schema_local_data.validate(self.destination_local)

      if not self.validate_container_size():
        raise HTTPException(status_code=499, detail="incorrect container size")
      if not self.validate_container_type():
        raise HTTPException(status_code=499, detail="incorrect container type")
      if not self.validate_commodity():
        raise HTTPException(status_code=499, detail="incorrect commodity")
      if not self.valid_uniqueness():
        raise HTTPException(status_code=499, detail="uniqueness not valid")

      self.set_omp_dmp_sl_sp()
      self.validate_origin_local()
      # self.validate_destination_local()
      if self.validate_origin_main_port_id():
        raise HTTPException(status_code=499, detail="origin main port id is invalid")
      if self.validate_destination_main_port_id():
        raise HTTPException(status_code=499, detail="destination main port id is invalid")

    def possible_origin_local_charge_codes(self):
      self.port = self.origin_port
      with open('src/charges/fcl_freight_local_charges.yml', 'r') as file:
        fcl_freight_local_charges_dict = yaml.safe_load(file)

      charge_codes = {}
      for k,v in fcl_freight_local_charges_dict.items():
          if eval(str(v['condition'])) and 'export' in v['trade_types']:
              charge_codes[k] = v
      return charge_codes

    def possible_destination_local_charge_codes(self):
      self.port = self.destination_port
      with open('src/charges/fcl_freight_local_charges.yml', 'r') as file:
        fcl_freight_local_charges_dict = yaml.safe_load(file)

      charge_codes = {}
      for k,v in fcl_freight_local_charges_dict.items():
          if eval(str(v['condition'])) and 'import' in v['trade_types']:
              charge_codes[k] = v
      return charge_codes

    def possible_charge_codes(self):  # check what to return
      with open('src/charges/fcl_freight_charges.yml', 'r') as file:
        fcl_freight_charges = yaml.safe_load(file)

      for k,v in fcl_freight_charges.items():
          if eval(str(v['condition'])):
              self.charge_codes[k] = v

    def is_rate_expired(self):
      if self.last_rate_available_date is None:
          return None
      else:
          return self.last_rate_available_date.date() < datetime.datetime.now().date()

    def is_rate_about_to_expire(self):
      if self.last_rate_available_date is None:
          return None
      else:
          return self.last_rate_available_date.date() < (datetime.datetime.now() + datetime.timedelta(days=2)).date()

    def is_rate_not_available(self):
      return self.last_rate_available_date is None


    def local_data_get_line_item_messages(self):

      location_ids = list(set([item["location_id"] for item in self.origin_local["line_items"] if item["location_id"] is not None]))
      
      locations = {}

      if location_ids:
        obj = {"filters" : {"id": location_ids}}
        locations = client.ruby.list_locations(obj)['list']
      return locations

    def update_local_references(self):
      local_objects = FclFreightRateLocal.select().where(
        (FclFreightRateLocal.port_id in [self.origin_port_id, self.destination_port_id]),
        (FclFreightRateLocal.main_port_id in [self.origin_main_port_id, self.destination_main_port_id]),
        (FclFreightRateLocal.container_size == self.container_size),
        (FclFreightRateLocal.container_type == self.container_type),
        (FclFreightRateLocal.commodity == (self.commodity if self.commodity in HAZ_COMMODITIES else None)),
        (FclFreightRateLocal.service_provider_id == self.service_provider_id),
        (FclFreightRateLocal.shipping_line_id == self.shipping_line_id)
      )

      filtered_objects = [t for t in local_objects if t.port_id == self.origin_port_id and t.main_port_id == self.origin_main_port_id and t.trade_type == 'export']

      origin_local_object_id = filtered_objects[0]['id'] if filtered_objects else None

      filtered_objects = [t for t in local_objects if t.port_id == self.destination_port_id and t.main_port_id == self.destination_main_port_id and t.trade_type == 'import']

      destination_local_object_id = filtered_objects[0]['id'] if filtered_objects else None

      self.update(origin_local_id = origin_local_object_id, destination_local_id = destination_local_object_id)

    def detail(self):

      data = {
          'freight': {
              'id': self.id,
              'validities': self.validities,
              'is_best_price': self.is_best_price,
              'is_rate_expired': self.is_rate_expired(),
              'is_rate_about_to_expire': self.is_rate_about_to_expire(),
              'is_rate_not_available': self.is_rate_not_available()
          },
          'weight_limit': dict(self.weight_limit)}

      data = {k: v for k, v in data.items()}

      origin_local = {}
      destination_local = {}

      if not self.port_origin_local['is_line_items_error_messages_present']:
          origin_local['line_items'] = list(self.port_origin_local['data']['line_items'])
          origin_local['is_line_items_error_messages_present'] = self.port_origin_local.is_line_items_error_messages_present
          origin_local['line_items_error_messages'] = self.port_origin_local.line_items_error_messages
          origin_local['is_line_items_info_messages_present'] = self.port_origin_local.is_line_items_info_messages_present
          origin_local['line_items_info_messages'] = self.port_origin_local.line_items_info_messages

      if not origin_local.get('line_items') or not self.is_origin_local_line_items_error_messages_present:
          origin_local['line_items'] = list(self.origin_local['line_items'])
          origin_local['is_line_items_error_messages_present'] = self.is_origin_local_line_items_error_messages_present
          origin_local['line_items_error_messages'] = self.origin_local_line_items_error_messages
          origin_local['is_line_items_info_messages_present'] = self.is_origin_local_line_items_info_messages_present
          origin_local['line_items_info_messages'] = self.origin_local_line_items_info_messages

      if self.origin_local.get('detention', {}).get('free_limit'):
        origin_local['detention'] = self.origin_local.detention.update(
          {'is_slabs_missing': self.is_origin_detention_slabs_missing})

      if not origin_local.get('detention'):
        port_origin_local_dict = dict(self.port_origin_local)
        origin_local['detention'] = port_origin_local_dict['data'].get('detention', {}).copy()
        origin_local['detention']['is_slabs_missing'] = port_origin_local_dict.get('is_detention_slabs_missing', False)

      if self.origin_local.as_json.get('demurrage', {}).get('free_limit'):
        origin_local['demurrage'] = dict(self.origin_local)['demurrage'].update(
          {'is_slabs_missing': self.is_origin_demurrage_slabs_missing})

      if not origin_local.get('demurrage'):
        port_origin_local_dict = dict(self.port_origin_local)
        origin_local['demurrage'] = port_origin_local_dict['data'].get('demurrage', {}).copy()
        origin_local['demurrage']['is_slabs_missing'] = port_origin_local_dict.get('is_demurrage_slabs_missing', False)

      if dict(self.origin_local).get('plugin', {}).get('free_limit') is not None:
        origin_local['plugin'] = dict(self.origin_local)['plugin']
        origin_local['plugin']['is_slabs_missing'] = self.is_origin_plugin_slabs_missing

      if not origin_local.get('plugin'):
        plugin_data = dict(self.port_origin_local).get('data', {}).get('plugin', {})
        plugin_slabs_missing = dict(self.port_origin_local).get('is_plugin_slabs_missing')
        origin_local['plugin'] = {**plugin_data, 'is_slabs_missing': plugin_slabs_missing}

      if not self.port_destination_local['is_line_items_error_messages_present']:
          destination_local['line_items'] = list(self.port_destination_local['data']['line_items'])
          destination_local['is_line_items_error_messages_present'] = self.port_destination_local.is_line_items_error_messages_present
          destination_local['line_items_error_messages'] = self.port_destination_local.line_items_error_messages
          destination_local['is_line_items_info_messages_present'] = self.port_destination_local.is_line_items_info_messages_present
          destination_local['line_items_info_messages'] = self.port_destination_local.line_items_info_messages

      if not destination_local.get('line_items') or not self.is_destination_local_line_items_error_messages_present:
          destination_local['line_items'] = list(self.destination_local['line_items'])
          destination_local['is_line_items_error_messages_present'] = self.is_destination_local_line_items_error_messages_present
          destination_local['line_items_error_messages'] = self.destination_local_line_items_error_messages
          destination_local['is_line_items_info_messages_present'] = self.is_destination_local_line_items_info_messages_present
          destination_local['line_items_info_messages'] = self.destination_local_line_items_info_messages

      if self.destination_local.get('detention', {}).get('free_limit'):
        destination_local['detention'] = self.destination_local.detention.update(
          {'is_slabs_missing': self.is_destination_detention_slabs_missing})

      if not destination_local.get('detention'):
        port_destination_local_dict = dict(self.port_destination_local)
        destination_local['detention'] = port_destination_local_dict['data'].get('detention', {}).copy()
        destination_local['detention']['is_slabs_missing'] = port_destination_local_dict.get('is_detention_slabs_missing', False)

      if self.destination_local.as_json.get('demurrage', {}).get('free_limit'):
        destination_local['demurrage'] = dict(self.destination_local)['demurrage'].update(
          {'is_slabs_missing': self.is_destination_demurrage_slabs_missing})

      if not destination_local.get('demurrage'):
        port_destination_local_dict = dict(self.port_destination_local)
        destination_local['demurrage'] = port_destination_local_dict['data'].get('demurrage', {}).copy()
        destination_local['demurrage']['is_slabs_missing'] = port_destination_local_dict.get('is_demurrage_slabs_missing', False)

      if dict(self.destination_local).get('plugin', {}).get('free_limit') is not None:
        destination_local['plugin'] = dict(self.destination_local)['plugin']
        destination_local['plugin']['is_slabs_missing'] = self.is_destination_plugin_slabs_missing

      if not destination_local.get('plugin'):
        plugin_data = dict(self.port_destination_local).get('data', {}).get('plugin', {})
        plugin_slabs_missing = dict(self.port_destination_local).get('is_plugin_slabs_missing')
        destination_local['plugin'] = {**plugin_data, 'is_slabs_missing': plugin_slabs_missing}
      
      if not origin_local['detention'].get('free_limit'):
        origin_local['detention'].update({'free_limit': DEFAULT_EXPORT_DESTINATION_DETENTION})

      if not destination_local['detention'].get('free_limit'):
        destination_local['detention'].update({'free_limit': DEFAULT_IMPORT_DESTINATION_DETENTION})

      return {**data, 'origin_local': origin_local, 'destination_local': destination_local}


    def update_fcl_freight_rate_platform_prices(self, origin_port_id, origin_main_port_id, destination_port_id, destination_main_port_id, container_size, container_type, commodity, shipping_line_id, importer_exporter_id):
      freight_objects = FclFreightRate.select().where(
        (FclFreightRate.origin_port_id == origin_port_id),
        (FclFreightRate.origin_main_port_id == origin_main_port_id if origin_main_port_id is not None else True),
        (FclFreightRate.destination_port_id == destination_port_id),
        (FclFreightRate.destination_main_port_id == destination_main_port_id if destination_main_port_id is not None else True),
        (FclFreightRate.container_size == container_size),
        (FclFreightRate.container_type == container_type),
        (FclFreightRate.commodity == commodity),
        (FclFreightRate.shipping_line_id == shipping_line_id)
      ).where(FclFreightRate.importer_exporter_id.in_([None, importer_exporter_id])
      ).where((FclFreightRate.last_rate_available_date >= date.today())).order_by(fn.Random())

      for freight in freight_objects:
        freight.set_platform_prices()
        freight.set_is_best_price()
        freight.save()

    # def update_priority_score(self): # check apis UpdateFclFreightRatePriorityScores
    #   UpdateFclFreightRatePriorityScores.run(filters={"id": self.id})

    def update_platform_prices_for_other_service_providers(self):  # check for delay
      #should be in delay
      self.update_fcl_freight_rate_platform_prices(self.origin_port_id, self.origin_main_port_id, self.destination_port_id, self.destination_main_port_id, self.container_size, self.container_type, self.commodity, self.shipping_line_id, self.importer_exporter_id)

    def create_trade_requirement_rate_mapping(self, procured_by_id, performed_by_id):
      if self.last_rate_available_date is None:
        return
    # api call and also expose

      current_app.send_task(
          "CreateOrganizationTradeRequirementRateMapping.run",
          queue="low",
          kwargs={
              "rate_id": self.id,
              "service": "fcl_freight",
              "performed_by_id": performed_by_id,
              "procured_by_id": procured_by_id,
              "last_updated_at": self.updated_at.replace(microsecond=0).isoformat(),
              "last_rate_available_date": self.last_rate_available_date.replace(microsecond=0).isoformat(),
              "price": self.get_price_for_trade_requirement(),
              "price_currency": "INR",
              "is_origin_local_missing": self.is_origin_local_missing,
              "is_destination_local_missing": self.is_destination_local_missing,
              "rate_params": {
                  "origin_location_id": self.origin_port_id,
                  "destination_location_id": self.destination_port_id,
                  "container_size": self.container_size,
                  "container_type": self.container_type,
                  "commodity": self.commodity,
              },
          },
      )


    def is_origin_local_missing(self):
      # return self.origin_local_id is None
      query = (FclFreightRate.select()
              .where(FclFreightRate.id == self.id,FclFreightRate.is_origin_local_line_items_error_messages_present << [None, True])
              .join(FclFreightRate.port_origin_local, JOIN.LEFT_OUTER)
              .where(FclFreightRateLocal.is_line_items_error_messages_present << [None, True])
              .exists())
      return query

    def is_destination_local_missing(self):
      # return self.destination_local_id is None
      query = (FclFreightRate.select()
              .where(FclFreightRate.id == self.id,FclFreightRate.is_destination_local_line_items_error_messages_present << [None, True])
              .join(FclFreightRate.port_destination_local, JOIN.LEFT_OUTER)
              .where(FclFreightRateLocal.is_line_items_error_messages_present << [None, True])
              .exists())
      return query

    def get_price_for_trade_requirement(self):  # check money exchange
      validity = self.validities.last()

      if validity is None:
        return 0
    
      result = GetMoneyExchange.run(price=validity.price, from_currency=validity.currency, to_currency="INR")
      return result["price"]


idx1 = FclFreightRate.index(FclFreightRate.origin_port_id, FclFreightRate.origin_main_port_id, FclFreightRate.destination_port_id, FclFreightRate.destination_main_port_id, FclFreightRate.container_size, FclFreightRate.container_type, FclFreightRate.commodity, FclFreightRate.shipping_line_id, FclFreightRate.service_provider_id, FclFreightRate.importer_exporter_id, unique=True).where(FclFreightRate.origin_main_port_id != None).where(FclFreightRate.destination_main_port_id != None).where(FclFreightRate.importer_exporter_id != None).where(FclFreightRate.cogo_entity_id == None)

idx2 = FclFreightRate.index(FclFreightRate.origin_port_id, FclFreightRate.origin_main_port_id, FclFreightRate.destination_port_id, FclFreightRate.destination_main_port_id, FclFreightRate.container_size, FclFreightRate.container_type, FclFreightRate.commodity, FclFreightRate.shipping_line_id, FclFreightRate.service_provider_id, FclFreightRate.importer_exporter_id, FclFreightRate.cogo_entity_id, unique=True).where(FclFreightRate.origin_main_port_id != None).where(FclFreightRate.destination_main_port_id != None).where(FclFreightRate.importer_exporter_id != None).where(FclFreightRate.cogo_entity_id != None)

idx3 = FclFreightRate.index(FclFreightRate.origin_port_id, FclFreightRate.origin_main_port_id, FclFreightRate.destination_port_id, FclFreightRate.destination_main_port_id, FclFreightRate.container_size, FclFreightRate.container_type, FclFreightRate.commodity, FclFreightRate.shipping_line_id, FclFreightRate.service_provider_id, FclFreightRate.cogo_entity_id, unique=True).where(FclFreightRate.origin_main_port_id != None).where(FclFreightRate.destination_main_port_id != None).where(FclFreightRate.importer_exporter_id == None).where(FclFreightRate.cogo_entity_id != None)

idx4 = FclFreightRate.index(FclFreightRate.origin_port_id, FclFreightRate.origin_main_port_id, FclFreightRate.destination_port_id, FclFreightRate.destination_main_port_id, FclFreightRate.container_size, FclFreightRate.container_type, FclFreightRate.commodity, FclFreightRate.shipping_line_id, FclFreightRate.service_provider_id, unique=True).where(FclFreightRate.origin_main_port_id != None).where(FclFreightRate.destination_main_port_id != None).where(FclFreightRate.importer_exporter_id == None).where(FclFreightRate.cogo_entity_id == None)

idx5 = FclFreightRate.index(FclFreightRate.origin_port_id, FclFreightRate.origin_main_port_id, FclFreightRate.destination_port_id, FclFreightRate.container_size, FclFreightRate.container_type, FclFreightRate.commodity, FclFreightRate.shipping_line_id, FclFreightRate.service_provider_id, FclFreightRate.importer_exporter_id,  FclFreightRate.cogo_entity_id, unique=True).where(FclFreightRate.origin_main_port_id != None).where(FclFreightRate.destination_main_port_id == None).where(FclFreightRate.importer_exporter_id == None).where(FclFreightRate.cogo_entity_id != None)

idx6 = FclFreightRate.index(FclFreightRate.origin_port_id, FclFreightRate.origin_main_port_id, FclFreightRate.destination_port_id, FclFreightRate.container_size, FclFreightRate.container_type, FclFreightRate.commodity, FclFreightRate.shipping_line_id, FclFreightRate.service_provider_id, FclFreightRate.importer_exporter_id, unique=True).where(FclFreightRate.origin_main_port_id != None).where(FclFreightRate.destination_main_port_id == None).where(FclFreightRate.importer_exporter_id == None).where(FclFreightRate.cogo_entity_id == None)

idx7 = FclFreightRate.index(FclFreightRate.origin_port_id, FclFreightRate.origin_main_port_id, FclFreightRate.destination_port_id, FclFreightRate.container_size, FclFreightRate.container_type, FclFreightRate.commodity, FclFreightRate.shipping_line_id, FclFreightRate.service_provider_id, FclFreightRate.cogo_entity_id, unique=True).where(FclFreightRate.origin_main_port_id != None).where(FclFreightRate.destination_main_port_id == None).where(FclFreightRate.importer_exporter_id == None).where(FclFreightRate.cogo_entity_id != None)

idx8 = FclFreightRate.index(FclFreightRate.origin_port_id, FclFreightRate.origin_main_port_id, FclFreightRate.destination_port_id, FclFreightRate.container_size, FclFreightRate.container_type, FclFreightRate.commodity, FclFreightRate.shipping_line_id, FclFreightRate.service_provider_id, unique=True).where(FclFreightRate.origin_main_port_id != None).where(FclFreightRate.destination_main_port_id == None).where(FclFreightRate.importer_exporter_id == None).where(FclFreightRate.cogo_entity_id == None)

idx9 = FclFreightRate.index(FclFreightRate.origin_port_id, FclFreightRate.destination_port_id, FclFreightRate.destination_main_port_id, FclFreightRate.container_size, FclFreightRate.container_type, FclFreightRate.commodity, FclFreightRate.shipping_line_id, FclFreightRate.service_provider_id, FclFreightRate.importer_exporter_id, FclFreightRate.cogo_entity_id, unique=True).where(FclFreightRate.origin_main_port_id == None).where(FclFreightRate.destination_main_port_id != None).where(FclFreightRate.importer_exporter_id != None).where(FclFreightRate.cogo_entity_id != None)

idx10 = FclFreightRate.index(FclFreightRate.origin_port_id, FclFreightRate.destination_port_id, FclFreightRate.destination_main_port_id, FclFreightRate.container_size, FclFreightRate.container_type, FclFreightRate.commodity, FclFreightRate.shipping_line_id, FclFreightRate.service_provider_id, FclFreightRate.cogo_entity_id, unique=True).where(FclFreightRate.origin_main_port_id == None).where(FclFreightRate.destination_main_port_id != None).where(FclFreightRate.importer_exporter_id == None).where(FclFreightRate.cogo_entity_id != None)

idx11 = FclFreightRate.index(FclFreightRate.origin_port_id, FclFreightRate.destination_port_id, FclFreightRate.destination_main_port_id, FclFreightRate.container_size, FclFreightRate.container_type, FclFreightRate.commodity, FclFreightRate.shipping_line_id, FclFreightRate.service_provider_id, unique=True).where(FclFreightRate.origin_main_port_id == None).where(FclFreightRate.destination_main_port_id != None).where(FclFreightRate.importer_exporter_id == None).where(FclFreightRate.cogo_entity_id == None)

idx12 = FclFreightRate.index(FclFreightRate.origin_port_id, FclFreightRate.destination_port_id, FclFreightRate.container_size, FclFreightRate.container_type, FclFreightRate.commodity, FclFreightRate.shipping_line_id, FclFreightRate.service_provider_id, FclFreightRate.importer_exporter_id, FclFreightRate.cogo_entity_id, unique=True).where(FclFreightRate.origin_main_port_id == None).where(FclFreightRate.destination_main_port_id == None).where(FclFreightRate.importer_exporter_id != None).where(FclFreightRate.cogo_entity_id != None)

idx13 = FclFreightRate.index(FclFreightRate.origin_port_id, FclFreightRate.destination_port_id, FclFreightRate.container_size, FclFreightRate.container_type, FclFreightRate.commodity, FclFreightRate.shipping_line_id, FclFreightRate.service_provider_id, FclFreightRate.importer_exporter_id, unique=True).where(FclFreightRate.origin_main_port_id == None).where(FclFreightRate.destination_main_port_id == None).where(FclFreightRate.importer_exporter_id != None).where(FclFreightRate.cogo_entity_id == None)

idx14 = FclFreightRate.index(FclFreightRate.origin_port_id, FclFreightRate.destination_port_id, FclFreightRate.container_size, FclFreightRate.container_type, FclFreightRate.commodity, FclFreightRate.shipping_line_id, FclFreightRate.service_provider_id, FclFreightRate.cogo_entity_id, unique=True).where(FclFreightRate.origin_main_port_id == None).where(FclFreightRate.destination_main_port_id == None).where(FclFreightRate.importer_exporter_id == None).where(FclFreightRate.cogo_entity_id != None)

idx15 = FclFreightRate.index(FclFreightRate.origin_port_id, FclFreightRate.destination_port_id, FclFreightRate.container_size, FclFreightRate.container_type, FclFreightRate.commodity, FclFreightRate.shipping_line_id, FclFreightRate.service_provider_id, unique=True).where(FclFreightRate.origin_main_port_id == None).where(FclFreightRate.destination_main_port_id == None).where(FclFreightRate.importer_exporter_id == None).where(FclFreightRate.cogo_entity_id == None)

FclFreightRate.add_index(idx1)
FclFreightRate.add_index(idx2)
FclFreightRate.add_index(idx3)
FclFreightRate.add_index(idx4)
FclFreightRate.add_index(idx5)
FclFreightRate.add_index(idx6)
FclFreightRate.add_index(idx7)
FclFreightRate.add_index(idx8)
FclFreightRate.add_index(idx9)
FclFreightRate.add_index(idx10)
FclFreightRate.add_index(idx11)
FclFreightRate.add_index(idx12)
FclFreightRate.add_index(idx13)
FclFreightRate.add_index(idx14)
FclFreightRate.add_index(idx15)

#  FclFreightRate.cogo_entity_id

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

    class Config:
        orm_mode = True
        exclude = ('validity_start', 'validity_end')