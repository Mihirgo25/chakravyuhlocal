from peewee import *
import datetime
from database.db_session import db
from playhouse.postgres_ext import *
from fastapi import HTTPException
from params import LineItem
from services.fcl_freight_rate.models.fcl_freight_rate_local import FclFreightRateLocal
from configs.fcl_freight_rate_constants import *
from schema import Schema, Optional
from configs.defintions import FCL_FREIGHT_CHARGES,FCL_FREIGHT_LOCAL_CHARGES,FCL_FREIGHT_CURRENCIES
from services.fcl_freight_rate.models.fcl_freight_rate_local_data import FclFreightRateLocalData
from services.fcl_freight_rate.models.fcl_freight_rate_free_day import FclFreightRateFreeDay
from services.fcl_freight_rate.models.fcl_freight_rate_free_day import FclFreightRateFreeDay
from configs.global_constants import DEFAULT_EXPORT_DESTINATION_DETENTION, DEFAULT_IMPORT_DESTINATION_DETENTION
from services.fcl_freight_rate.interaction.update_fcl_freight_rate_platform_prices import update_fcl_freight_rate_platform_prices
from configs.global_constants import HAZ_CLASSES
from micro_services.client import *
class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True
       
class FclFreightRate(BaseModel):
    commodity = CharField(null=True, index=True)
    container_size = CharField(null=True, index=True)
    container_type = CharField(null=True, index=True)
    containers_count = IntegerField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    destination_continent_id = UUIDField(null=True)
    destination_country_id = UUIDField(null=True)
    destination_local = BinaryJSONField(null=True)
    destination_local_id = ForeignKeyField(FclFreightRateLocal, index=True, null=True)
    destination_detention_id = ForeignKeyField(FclFreightRateFreeDay, index=True, null=True)
    destination_demurrage_id = ForeignKeyField(FclFreightRateFreeDay, index=True, null=True)
    destination_local_line_items_error_messages = BinaryJSONField(constraints=[SQL("DEFAULT '{}'::jsonb")], null=True)
    destination_local_line_items_info_messages = BinaryJSONField(constraints=[SQL("DEFAULT '{}'::jsonb")], null=True)
    destination_location_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, index=True, null=True)
    destination_main_port_id = UUIDField(null=True, index=True)
    destination_main_port = BinaryJSONField(null=True)
    destination_plugin_id = UUIDField(index=True, null=True)
    destination_port_id = UUIDField(index=True, null=True)
    destination_port = BinaryJSONField(null=True)
    destination_trade_id = UUIDField(null=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    importer_exporter_id = UUIDField(null=True)
    importer_exporter = BinaryJSONField(null=True)
    importer_exporters_count = IntegerField(null=True)
    is_best_price = BooleanField(null=True)
    is_destination_demurrage_slabs_missing = BooleanField(null=True)
    is_destination_detention_slabs_missing = BooleanField(null=True)
    is_destination_local_line_items_error_messages_present = BooleanField(null=True)
    is_destination_local_line_items_info_messages_present = BooleanField(null=True)
    is_destination_plugin_slabs_missing = BooleanField(null=True)
    is_origin_demurrage_slabs_missing = BooleanField(null=True)
    is_origin_detention_slabs_missing = BooleanField(null=True)
    is_origin_local_line_items_error_messages_present = BooleanField(null=True)
    is_origin_local_line_items_info_messages_present = BooleanField(null=True)
    is_origin_plugin_slabs_missing = BooleanField(null=True)
    is_weight_limit_slabs_missing = BooleanField(null=True)
    last_rate_available_date = DateField(null=True, index=True)
    omp_dmp_sl_sp = CharField(null=True)
    origin_continent_id = UUIDField(null=True)
    origin_country_id = UUIDField(null=True)
    origin_local = BinaryJSONField(null=True)
    origin_local_id = ForeignKeyField(FclFreightRateLocal, index=True, null=True)
    origin_detention_id = ForeignKeyField(FclFreightRateFreeDay, index=True, null=True)
    origin_demurrage_id = ForeignKeyField(FclFreightRateFreeDay, index=True, null=True)
    origin_local_line_items_error_messages = BinaryJSONField(constraints=[SQL("DEFAULT '{}'::jsonb")], null=True)
    origin_local_line_items_info_messages = BinaryJSONField(constraints=[SQL("DEFAULT '{}'::jsonb")], null=True)
    origin_location_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, index=True, null=True)
    origin_main_port_id = UUIDField(null=True, index=True)
    origin_main_port = BinaryJSONField(null=True)
    origin_plugin_id = UUIDField(index=True, null=True)
    origin_port_id = UUIDField(null=True, index=True)
    origin_port = BinaryJSONField(null=True)
    origin_trade_id = UUIDField(null=True)
    rate_not_available_entry = BooleanField(constraints=[SQL("DEFAULT false")], null=True)
    service_provider_id = UUIDField(index=True, null=True)
    service_provider = BinaryJSONField(null=True)
    shipping_line = BinaryJSONField(null=True)
    shipping_line_id = UUIDField(index=True, null=True)
    updated_at = DateTimeField(default=datetime.datetime.now, index=True)
    validities = BinaryJSONField(default = [], null=True)
    weight_limit = BinaryJSONField(null=True)
    weight_limit_id = UUIDField(index=True, null=True)
    mode = CharField(default = 'manual', null = True)
    accuracy = FloatField(default = 100, null = True)
    cogo_entity_id = UUIDField(index=True, null=True)
    sourced_by_id = UUIDField(null=True, index=True)
    procured_by_id = UUIDField(null=True, index=True)
    sourced_by = BinaryJSONField(null=True)
    procured_by = BinaryJSONField(null=True)
    init_key = TextField(index=True)
    sourced_by = BinaryJSONField(null=True)
    procured_by = BinaryJSONField(null=True)
    
    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(FclFreightRate, self).save(*args, **kwargs)

    class Meta:
        table_name = 'fcl_freight_rates'

    def set_locations(self):

      obj = {'filters':{"id": [str(self.origin_port_id), str(self.destination_port_id), str(self.origin_main_port_id), str(self.destination_main_port_id)],"type":'seaport'}}
      locations = maps.list_locations(obj)['list']
      

      for location in locations:
        if str(self.origin_port_id) == str(location['id']):
          self.origin_port = self.get_required_location_data(location)
        if str(self.destination_port_id) == str(location['id']):
          self.destination_port = self.get_required_location_data(location)
        if str(self.origin_main_port_id) == str(location['id']):
          self.origin_main_port = self.get_required_location_data(location)
        if str(self.destination_main_port_id) == str(location['id']):
          self.destination_main_port = self.get_required_location_data(location)

    def get_required_location_data(self, location):
        loc_data = {
          "id": location["id"],
          "name": location["name"],
          "is_icd": location["is_icd"],
          "port_code": location["port_code"],
          "country_id": location["country_id"],
          "continent_id": location["continent_id"],
          "trade_id": location["trade_id"],
          "country_code": location["country_code"]
        }
        return loc_data
      
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
        if not self.origin_main_port_id or self.origin_main_port_id!=self.origin_port_id:
          return True
        return False
      elif self.origin_port and self.origin_port['is_icd']==True and not self.rate_not_available_entry:

        if self.origin_main_port_id:
          if not self.origin_main_port or self.origin_main_port['is_icd']==True:
            return False
        else:
          return False
      return True

    def validate_destination_main_port_id(self):
      if self.destination_port and self.destination_port['is_icd'] == False:
        if not self.destination_main_port_id or self.destination_main_port_id!=self.destination_port_id:
          return True
        return False
      elif self.destination_port and self.destination_port['is_icd']==True and not self.rate_not_available_entry:
        if self.destination_main_port_id:
          if not self.destination_main_port or self.destination_main_port['is_icd']==True:
            return False
        else:
          return False
      return True

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

    def set_omp_dmp_sl_sp(self):
      self.omp_dmp_sl_sp = ":".join([str(self.origin_main_port_id or ""), str(self.destination_main_port_id or ""), str(self.shipping_line_id), str(self.service_provider_id)])

    def update_special_attributes(self):
      self.update_origin_local_line_item_messages()
      self.update_destination_local_line_item_messages()
      self.update_origin_free_days_special_attributes()
      self.update_destination_free_days_special_attributes()
      self.update_weight_limit_special_attributes()

    def update_origin_local_line_item_messages(self):

      if self.origin_local:
        self.origin_local_data_instance = FclFreightRateLocalData(self.origin_local)
        response = self.origin_local_data_instance.get_line_item_messages(self.origin_port,self.origin_main_port,self.shipping_line,self.container_size,self.container_type,self.commodity,'export',self.possible_origin_local_charge_codes())
        response={}

      self.origin_local_line_items_error_messages = response.get('line_items_error_messages'),
      self.is_origin_local_line_items_error_messages_present = response.get('is_line_items_error_messages_present'),
      self.origin_local_line_items_info_messages = response.get('line_items_info_messages'),
      self.is_origin_local_line_items_info_messages_present = response.get('is_line_items_info_messages_present')

    def update_destination_local_line_item_messages(self):

      if self.destination_local:
        response = FclFreightRateLocalData(self.destination_local)
        response = self.origin_local_data_instance.get_line_item_messages(self.destination_port,self.destination_main_port,self.shipping_line,self.container_size,self.container_type,self.commodity,'export',self.possible_origin_local_charge_codes())
        response={}

      self.destination_local_line_items_error_messages = response.get('line_items_error_messages'),
      self.is_destination_local_line_items_error_messages_present = response.get('is_line_items_error_messages_present'),
      self.destination_local_line_items_info_messages = response.get('line_items_info_messages'),
      self.is_destination_local_line_items_info_messages_present = response.get('is_line_items_info_messages_present')


    def update_origin_free_days_special_attributes(self):
      self.is_origin_detention_slabs_missing = (len(self.origin_detention.get('slabs',{})) == 0) if self.origin_detention.get("slabs") is not None else True,
      self.is_origin_demurrage_slabs_missing = (len(self.origin_demurrage.get('slabs',{})) == 0) if self.origin_demurrage.get("slabs") is not None else True,
      self.is_origin_plugin_slabs_missing = (len(self.origin_local.get('plugin',{}).get('slabs',{})) == 0) if self.origin_local.get("plugin") is not None else True


    def update_destination_free_days_special_attributes(self):
      self.is_destination_detention_slabs_missing = (len(self.destination_detention.get('slabs',{})) == 0) if self.destination_detention.get("slabs") is not None else True,
      self.is_destination_demurrage_slabs_missing = (len(self.destination_demurrage.get('slabs',{})) == 0) if self.destination_demurrage.get("slabs") is not None else True,
      self.is_destination_plugin_slabs_missing = (len(self.destination_local.get('plugin',{}).get('slabs',{})) == 0) if self.destination_local.get("plugin") is not None else True


    def update_weight_limit_special_attributes(self):
      if self.weight_limit:
        self.is_weight_limit_slabs_missing = (len(self.weight_limit.get('slabs',[])) == 0)
      else:
        self.is_weight_limit_slabs_missing = True

    def validate_origin_local(self):
      if 'origin_local' in self.dirty_fields and self.origin_local:
        duplicate = self.origin_local_instance.validate_duplicate_charge_codes()
        invalid = self.origin_local_instance.validate_invalid_charge_codes(self.possible_origin_local_charge_codes())
        if not  (duplicate and invalid):
          raise HTTPException(status_code=404,detail="Origin Local Invalid")


    def validate_destination_local(self):
      if 'destination_local' in self.dirty_fields and self.destination_local:
        duplicate = self.destination_local_instance.validate_duplicate_charge_codes()
        invalid = self.destination_local_instance.validate_invalid_charge_codes(self.possible_destination_local_charge_codes())

      if not (duplicate and invalid):
          raise HTTPException(status_code=404,detail="Destination Local Invalid")

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

      
      fcl_freight_charges_dict = FCL_FREIGHT_CHARGES

      invalid_line_items = [code for code in codes if code not in fcl_freight_charges_dict.keys()]
      
      if invalid_line_items:
          raise HTTPException(status_code=499, detail="line_items {} are invalid".format(", ".join(invalid_line_items)))

      fcl_freight_currencies = FCL_FREIGHT_CURRENCIES

      currencies = [currency for currency in fcl_freight_currencies]
      line_item_currencies = [item['currency'] for item in line_items]

      if any(currency not in currencies for currency in line_item_currencies):
        raise HTTPException(status_code=499, detail='line_item_currency is invalid')

      mandatory_codes = []

      origin_port = self.origin_port
      destination_port = self.destination_port
      shipping_line_id = self.shipping_line_id
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
            ).where(FclFreightRate.importer_exporter_id.in_([None, self.importer_exporter_id])).where(((FclFreightRate.service_provider_id != self.service_provider_id) | (FclFreightRate.service_provider_id.is_null(True)))).execute()

      result = price
      if freight_rates:
        for freight_rate in freight_rates:
          validities = []

          for t in freight_rate.validities:
            if (validity_start <= t["validity_end"]) & (validity_end >= t["validity_start"]):
              validities.append(t)

          for t in validities:
            price = []
            new_price =  common.get_money_exchange_for_fcl({'price': t["price"], 'from_currency': t['currency'], 'to_currency':currency})['price']
            price.append(new_price)
            freight_rate_min_price = min(price)

          if freight_rate_min_price < result  and freight_rate_min_price is not None:      
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
            currency_lists = [item["currency"] for item in line_items if item["code"] == "BAS"]
            currency = currency_lists[0]
            if len(set(currency_lists)) != 1:
                price = float(sum(common.get_money_exchange_for_fcl({"price": item['price'], "from_currency": item['currency'], "to_currency": currency}).get('price', 100) for item in line_items))
            else:
                price = float(sum(item["price"] for item in line_items))
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
                new_validities.append(FclFreightRateValidity(**validity_object))
                continue
            if (validity_object['payment_term'] not in [None, payment_term] and not deleted):
                new_validities.append(FclFreightRateValidity(**validity_object))
                continue
            if validity_object_validity_start > validity_end:
                new_validities.append(FclFreightRateValidity(**validity_object))
                continue
            if validity_object_validity_end < validity_start:
                new_validities.append(FclFreightRateValidity(**validity_object))
                continue
            if validity_object_validity_start >= validity_start and validity_object_validity_end <= validity_end:
                continue
            if validity_object_validity_start < validity_start and validity_object_validity_end <= validity_end:
                validity_object_validity_end = validity_start - datetime.timedelta(days=1)
                new_validities.append(FclFreightRateValidity(**validity_object))
                continue
            if validity_object_validity_start >= validity_start and validity_object_validity_end > validity_end:
                validity_object_validity_start = validity_end + datetime.timedelta(days=1)
                new_validities.append(FclFreightRateValidity(**validity_object))
                continue
            if validity_object_validity_start < validity_start and validity_object_validity_end > validity_end:
                new_validities.append(FclFreightRateValidity(**{**validity_object, 'validity_end': validity_start - datetime.timedelta(days=1)}))
                new_validities.append(FclFreightRateValidity(**{**validity_object, 'validity_start': validity_end + datetime.timedelta(days=1)}))
                continue

        new_validities = [validity for validity in new_validities if datetime.datetime.strptime(str(validity.validity_end), '%Y-%m-%d').date() >= datetime.datetime.now().date()]
        new_validities = sorted(new_validities, key=lambda validity: datetime.datetime.strptime(str(validity.validity_start), '%Y-%m-%d').date())

        main_validities=[]
        for new_validity in new_validities:          
          new_validity.line_items = [dict(line_item) for line_item in new_validity.line_items]
          new_validity.validity_start = datetime.datetime.strptime(str(new_validity.validity_start), '%Y-%m-%d').date().isoformat()
          new_validity.validity_end = datetime.datetime.strptime(str(new_validity.validity_end), '%Y-%m-%d').date().isoformat()
          new_validity = vars(new_validity)
          new_validity['id'] = new_validity['__data__']['id']
          new_validity.pop('__data__')
          new_validity.pop('__rel__')
          new_validity.pop('_dirty')
          main_validities.append(new_validity)
        
        self.validities = main_validities

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

    def validate_before_save(self):

      schema_weight_limit = Schema({'free_limit': float, Optional('slabs'): list, Optional('remarks'): list})
     
      if self.weight_limit:
        schema_weight_limit.validate(self.weight_limit)

        self.weight_limit['slabs'] = sorted(self.weight_limit['slabs'], key=lambda x: x['lower_limit'])

        if self.weight_limit['slabs'] and self.weight_limit['free_limit']!=0 and (self.weight_limit['free_limit'] >= self.weight_limit['slabs'][0]['lower_limit']):
          raise HTTPException(status_code=499, detail="slabs lower limit should be greater than free limit")

        for index, weight_limit_slab in enumerate(self.weight_limit['slabs']):
          if (weight_limit_slab['upper_limit'] <= weight_limit_slab['lower_limit']) or (index != 0 and weight_limit_slab['lower_limit'] <= self.weight_limit['slabs'][index - 1]['upper_limit']):
            raise HTTPException(status_code=499, detail="slabs are not valid")

      self.origin_local_instance = FclFreightRateLocalData(self.origin_local)

      self.destination_local_instance = FclFreightRateLocalData(self.destination_local)

      if not self.validate_container_size():
        raise HTTPException(status_code=499, detail="incorrect container size")
      if not self.validate_container_type():
        raise HTTPException(status_code=499, detail="incorrect container type")
      if not self.validate_commodity():
        raise HTTPException(status_code=499, detail="incorrect commodity")

      self.set_omp_dmp_sl_sp()
      self.validate_origin_local()
      self.validate_destination_local()
      
      if not self.validate_origin_main_port_id():
        raise HTTPException(status_code=499, detail="origin main port id is required")
      
      if not self.validate_destination_main_port_id():
        raise HTTPException(status_code=499, detail="destination main port id is required")

    def possible_origin_local_charge_codes(self):
      self.port = self.origin_port
      fcl_freight_local_charges_dict = FCL_FREIGHT_LOCAL_CHARGES

      charge_codes = {}
      port = self.origin_port
      main_port = self.origin_main_port
      shipping_line_id = self.shipping_line_id
      container_size = self.container_size
      container_type = self.container_type
      commodity = self.commodity

      for k,v in fcl_freight_local_charges_dict.items():
        if eval(str(v['condition'])) and 'export' in v['trade_types']:
            charge_codes[k] = v
      return charge_codes

    def possible_destination_local_charge_codes(self):
      self.port = self.destination_port
      fcl_freight_local_charges_dict = FCL_FREIGHT_LOCAL_CHARGES

      port = self.destination_port
      main_port = self.destination_main_port
      shipping_line_id = self.shipping_line_id
      container_size = self.container_size
      container_type = self.container_type
      commodity = self.commodity
      charge_codes = {}
      for k,v in fcl_freight_local_charges_dict.items():
          if eval(str(v['condition'])) and 'import' in v['trade_types']:
              charge_codes[k] = v
      return charge_codes

    def possible_charge_codes(self):  
      fcl_freight_charges = FCL_FREIGHT_CHARGES

      charge_codes = {}
      shipping_line_id = self.shipping_line_id
      container_size = self.container_size
      container_type = self.container_type
      commodity = self.commodity
      destination_port = self.destination_port

      for k,v in fcl_freight_charges.items():
          if eval(str(v['condition'])):
              charge_codes[k] = v
      return charge_codes

    def is_rate_expired(self):
      if self.last_rate_available_date is None:
          return None
      else:
          return self.last_rate_available_date < datetime.datetime.now().date()

    def is_rate_about_to_expire(self):
      if self.last_rate_available_date is None:
          return None
      else:
          return self.last_rate_available_date < (datetime.datetime.now() + datetime.timedelta(days=2)).date()

    def is_rate_not_available(self):
      return self.last_rate_available_date is None


    def local_data_get_line_item_messages(self):

      location_ids = list(set([item["location_id"] for item in self.origin_local["line_items"] if item["location_id"] is not None]))
      locations = {}

      if location_ids:
        obj = {'filters':{"id": location_ids}}
        locations = maps.list_locations(obj)['list']
        
      return locations

    def update_local_references(self):
      local_objects = FclFreightRateLocal.select().where(
        FclFreightRateLocal.port_id << (self.origin_port_id, self.destination_port_id),
        FclFreightRateLocal.main_port_id << (self.origin_main_port_id, self.destination_main_port_id) if self.origin_port_id !=self.origin_main_port_id or self.destination_port_id !=self.destination_main_port_id else FclFreightRateLocal.id.is_null(False),
        FclFreightRateLocal.container_size == self.container_size,
        FclFreightRateLocal.container_type == self.container_type,
        FclFreightRateLocal.commodity == self.commodity if self.commodity in HAZ_CLASSES else FclFreightRateLocal.id.is_null(False),
        FclFreightRateLocal.service_provider_id == self.service_provider_id,
        FclFreightRateLocal.shipping_line_id == self.shipping_line_id
      ).execute()

      filtered_objects = [t for t in local_objects if str(t.port_id) == str(self.origin_port_id) and str(t.main_port_id or '') == str(self.origin_main_port_id or '') and t.trade_type == 'export']

      origin_local_object_id = filtered_objects[0].id if filtered_objects else None

      filtered_objects = [t for t in local_objects if str(t.port_id) == str(self.destination_port_id) and str(t.main_port_id or '') == str(self.destination_main_port_id or '') and t.trade_type == 'import']

      destination_local_object_id = filtered_objects[0].id if filtered_objects else None
      FclFreightRate.update(origin_local_id = origin_local_object_id,destination_local_id=destination_local_object_id).where(
        FclFreightRate.id == self.id
      ).execute()

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

      if self.origin_local_id:
        if self.origin_local_id.is_line_items_error_messages_present == False:
          origin_local['line_items'] = self.origin_local_id.data['line_items']
          origin_local['is_line_items_error_messages_present'] = self.origin_local_id.is_line_items_error_messages_present
          origin_local['line_items_error_messages'] = self.origin_local_id.line_items_error_messages
          origin_local['is_line_items_info_messages_present'] = self.origin_local_id.is_line_items_info_messages_present
          origin_local['line_items_info_messages'] = self.origin_local_id.line_items_info_messages

      # if self.origin_local_id and (not self.origin_local_id.is_line_items_error_messages_present):
      #     origin_local['line_items'] = list(self.port_origin_local['data']['line_items'])
      #     origin_local['is_line_items_error_messages_present'] = self.port_origin_local.is_line_items_error_messages_present
      #     origin_local['line_items_error_messages'] = self.port_origin_local.line_items_error_messages
      #     origin_local['is_line_items_info_messages_present'] = self.port_origin_local.is_line_items_info_messages_present
      #     origin_local['line_items_info_messages'] = self.port_origin_local.line_items_info_messages

        if not origin_local.get('line_items') or not self.is_origin_local_line_items_error_messages_present:
            origin_local['line_items'] = self.origin_local['line_items']
            origin_local['is_line_items_error_messages_present'] = self.is_origin_local_line_items_error_messages_present
            origin_local['line_items_error_messages'] = self.origin_local_line_items_error_messages
            origin_local['is_line_items_info_messages_present'] = self.is_origin_local_line_items_info_messages_present
            origin_local['line_items_info_messages'] = self.origin_local_line_items_info_messages

        if 'detention' in self.origin_local and self.origin_local.get('detention'):
          if self.origin_local['detention'].get('free_limit'):
            origin_local['detention'] = self.origin_local['detention'] | ({'is_slabs_missing': self.is_origin_detention_slabs_missing })
          else:
            origin_local['detention'] = origin_local['detention'] | ({ 'free_limit': DEFAULT_EXPORT_DESTINATION_DETENTION })

        if not origin_local.get('detention'):
          origin_local['detention'] = self.origin_local_id.data['detention'] | ({'is_slabs_missing': self.origin_local_id.is_detention_slabs_missing})

        if 'demurrage' in self.origin_local and self.origin_local.get('demurrage'):
          if self.origin_local['demurrage'].get('free_limit'):
            origin_local['demurrage'] = self.origin_local['demurrage'] | ({'is_slabs_missing': self.is_origin_demurrage_slabs_missing })

        if not origin_local.get('demurrage'):
          origin_local['demurrage'] = self.origin_local_id.data['demurrage'] | ({'is_slabs_missing': self.origin_local_id.is_demurrage_slabs_missing})

        if 'plugin' in self.origin_local and self.origin_local.get('plugin'):
          if self.origin_local['plugin'].get('free_limit'):
            origin_local['plugin'] = self.origin_local['plugin'] | ({'is_slabs_missing': self.is_origin_plugin_slabs_missing })    

        if not origin_local['plugin']:
          origin_local['plugin'] = self.origin_local_id.data['plugin'] | ({'is_slabs_missing': self.origin_local_id.is_plugin_slabs_missing})

        # if self.origin_local_id.origin_detention.get('free_limit'):
        #   origin_local['detention'] = self.origin_detention.update(
        #     {'is_slabs_missing': self.is_origin_detention_slabs_missing})
        # if self.origin_demurrage.get('free_limit'):
        #   origin_local['demurrage'] = self.origin_demurrage.update(
        #     {'is_slabs_missing': self.is_origin_demurrage_slabs_missing})
      # if not origin_local.get('demurrage'):
      #   port_origin_local_dict = dict(self.port_origin_local)
      #   origin_local['demurrage'] = port_origin_local_dict['data'].get('demurrage', {}).copy()
      #   origin_local['demurrage']['is_slabs_missing'] = port_origin_local_dict.get('is_demurrage_slabs_missing', False)
      # if dict(self.origin_local).get('plugin', {}).get('free_limit') is not None:
      #   origin_local['plugin'] = dict(self.origin_local)['plugin']
      #   origin_local['plugin']['is_slabs_missing'] = self.is_origin_plugin_slabs_missing
      # if not origin_local.get('plugin'):
      #   plugin_data = dict(self.port_origin_local).get('data', {}).get('plugin', {})
      #   plugin_slabs_missing = dict(self.port_origin_local).get('is_plugin_slabs_missing')
      #   origin_local['plugin'] = {**plugin_data, 'is_slabs_missing': plugin_slabs_missing}

      if self.destination_local_id:
        if not self.destination_local_id.is_line_items_error_messages_present:
            destination_local['line_items'] = self.destination_local_id.data['line_items']
            destination_local['is_line_items_error_messages_present'] = self.destination_local_id.is_line_items_error_messages_present
            destination_local['line_items_error_messages'] = self.destination_local_id.line_items_error_messages
            destination_local['is_line_items_info_messages_present'] = self.destination_local_id.is_line_items_info_messages_present
            destination_local['line_items_info_messages'] = self.destination_local_id.line_items_info_messages

        if not destination_local.get('line_items') or not self.is_destination_local_line_items_error_messages_present:
            destination_local['line_items'] = self.destination_local['line_items']
            destination_local['is_line_items_error_messages_present'] = self.is_destination_local_line_items_error_messages_present
            destination_local['line_items_error_messages'] = self.destination_local_line_items_error_messages
            destination_local['is_line_items_info_messages_present'] = self.is_destination_local_line_items_info_messages_present
            destination_local['line_items_info_messages'] = self.destination_local_line_items_info_messages

        if 'detention' in self.destination_local and self.destination_local.get('detention'):
          if self.destination_local['detention'].get('free_limit'):
            destination_local['detention'] = self.destination_local['detention'] | ({'is_slabs_missing': self.is_destination_detention_slabs_missing })
          else:
            destination_local['detention'] = destination_local['detention'] | ({'free_limit': DEFAULT_IMPORT_DESTINATION_DETENTION })

        if not destination_local.get('detention'):
          if self.destination_local_id.data.get('detention'):
            destination_local['detention'] = self.destination_local_id.data['detention'] | ({'is_slabs_missing': self.destination_local_id.is_detention_slabs_missing})
          else:
            destination_local['detention'] = {'is_slabs_missing': self.destination_local_id.is_detention_slabs_missing}

        if 'demurrage' in self.destination_local and self.destination_local.get('demurrage'):
          if self.destination_local['demurrage'].get('free_limit'):
            destination_local['demurrage'] = self.destination_local['demurrage'] | ({'is_slabs_missing': self.is_destination_demurrage_slabs_missing })

        if not destination_local.get('demurrage'):
          if self.destination_local_id.data.get('demurrage'):
            destination_local['demurrage'] = self.destination_local_id.data['demurrage'] | ({'is_slabs_missing': self.destination_local_id.is_demurrage_slabs_missing})
          else:
            destination_local['demurrage'] = {'is_slabs_missing': self.destination_local_id.is_demurrage_slabs_missing}


        if 'plugin' in self.destination_local and self.destination_local.get('plugin'):
          if self.destination_local['plugin'].get('free_limit'):
            destination_local['plugin'] = self.destination_local['plugin'] | ({'is_slabs_missing': self.is_destination_plugin_slabs_missing })

        if not destination_local.get('plugin'):
          if self.destination_local_id.data.get('plugin'):
            destination_local['plugin'] = self.destination_local_id.data['plugin'] | ({'is_slabs_missing': self.destination_local_id.is_plugin_slabs_missing})
          else:
            destination_local['plugin'] = {'is_slabs_missing': self.destination_local_id.is_plugin_slabs_missing}
          
      # if destination_detention.get('free_limit'):
      #   destination_local['detention'] = self.destination_detention.update(
      #     {'is_slabs_missing': self.is_destination_detention_slabs_missing})
      # if not destination_local.get('detention'):
      #   port_destination_local_dict = dict(self.port_destination_local)
      #   destination_local['detention'] = port_destination_local_dict['data'].get('detention', {}).copy()
      #   destination_local['detention']['is_slabs_missing'] = port_destination_local_dict.get('is_detention_slabs_missing', False)
      # if self.destination_demurrage.get('free_limit'):
      #   destination_local['demurrage'] = self.destination_demurrage.update(
      #     {'is_slabs_missing': self.is_destination_demurrage_slabs_missing})
      # if not destination_local.get('demurrage'):
      #   port_destination_local_dict = dict(self.port_destination_local)
      #   destination_local['demurrage'] = port_destination_local_dict['data'].get('demurrage', {}).copy()
      #   destination_local['demurrage']['is_slabs_missing'] = port_destination_local_dict.get('is_demurrage_slabs_missing', False)
      # if dict(self.destination_local).get('plugin', {}).get('free_limit') is not None:
      #   destination_local['plugin'] = dict(self.destination_local)['plugin']
      #   destination_local['plugin']['is_slabs_missing'] = self.is_destination_plugin_slabs_missing
      # if not destination_local.get('plugin'):
      #   plugin_data = dict(self.port_destination_local).get('data', {}).get('plugin', {})
      #   plugin_slabs_missing = dict(self.port_destination_local).get('is_plugin_slabs_missing')
      #   destination_local['plugin'] = {**plugin_data, 'is_slabs_missing': plugin_slabs_missing}
      # if not self.origin_detention.get('free_limit'):
      #   origin_local['detention'].update({'free_limit': DEFAULT_EXPORT_DESTINATION_DETENTION})
      # if not self.destination_detention.get('free_limit'):
      #   destination_local['detention'].update({'free_limit': DEFAULT_IMPORT_DESTINATION_DETENTION})
      # if ('free_limit' in self.destination_local.get('demurrage',{})):
      #   if (self.destination_local['demurrage'].get('free_limit')):
      #      destination_local['demurrage'] = self.destination_local['demurrage'] | ({'is_slabs_missing': self.is_destination_demurrage_slabs_missing })
      # if not destination_local.get('demurrage'):
      #   destination_local['demurrage'] = self.destination_local_id.data['demurrage'] | ({'is_slabs_missing': self.destination_local_id.is_demurrage_slabs_missing})
      # if self.destination_local['plugin'] and ('free_limit' in self.destination_local.get('plugin', {})):
      #   if self.destination_local['demurrage'].get('free_limit'):
      #     destination_local['plugin'] = self.destination_local['plugin'] | ({'is_slabs_missing': self.is_destination_plugin_slabs_missing })
      # if not destination_local.get('plugin'):
      #   if self.destination_local_id.data.get('plugin', {}):
      #     destination_local['plugin'] = self.destination_local_id.data.get('plugin',{}) | ({'is_slabs_missing': self.destination_local_id.is_plugin_slabs_missing})
      #   else:
      #     destination_local['plugin'] = ({'is_slabs_missing': self.destination_local_id.is_plugin_slabs_missing})
      # if ('free_limit' in origin_local.get('detention',{})):
      #   if not origin_local.get('detention').get('free_limit'):
      #     origin_local['detention'] = origin_local['detention'] | ({'free_limit': DEFAULT_EXPORT_DESTINATION_DETENTION })
      # if 'free_limit' in destination_local.get('detention',{}):
      #   if not destination_local.get('detention').get('free_limit'):
      #     destination_local['detention'] = destination_local['detention'] | ({'free_limit': DEFAULT_IMPORT_DESTINATION_DETENTION })
      return {**data, 'origin_local': origin_local, 'destination_local': destination_local}



    def update_platform_prices_for_other_service_providers(self):  
      data = {
        "origin_port_id":self.origin_port_id,
        "origin_main_port_id":self.origin_main_port_id,
        "destination_port_id":self.destination_port_id,
        "destination_main_port_id":self.destination_main_port_id,
        "container_size":self.container_size,
        "container_type":self.container_type,
        "commodity":self.commodity,
        "shipping_line_id":self.shipping_line_id,
        "importer_exporter_id":self.importer_exporter_id
      }
      update_fcl_freight_rate_platform_prices(data)

    def create_trade_requirement_rate_mapping(self, procured_by_id, performed_by_id):
      if self.last_rate_available_date is None:

        return
      data={
              "rate_id": self.id,
              "service": "fcl_freight",
              "performed_by_id": performed_by_id,
              "procured_by_id": procured_by_id,
              "last_updated_at": self.updated_at.replace(microsecond=0).isoformat(),
              "last_rate_available_date": datetime.datetime.strptime(str(self.last_rate_available_date), '%Y-%m-%d').date().isoformat(),
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
              }
          }
    # api call and also expose
      # common.create_organization_trade_requirement_rate_mapping(data)



    def is_origin_local_missing(self):
      query = (FclFreightRate.select()
              .where(FclFreightRate.id == self.id,FclFreightRate.is_origin_local_line_items_error_messages_present << [None, True])
              .join(FclFreightRate.port_origin_local, JOIN.LEFT_OUTER)
              .where(FclFreightRateLocal.is_line_items_error_messages_present << [None, True])
              .exists())
      return query

    def is_destination_local_missing(self):
      query = (FclFreightRate.select()
              .where(FclFreightRate.id == self.id,FclFreightRate.is_destination_local_line_items_error_messages_present << [None, True])
              .join(FclFreightRate.port_destination_local, JOIN.LEFT_OUTER)
              .where(FclFreightRateLocal.is_line_items_error_messages_present << [None, True])
              .exists())
      return query

    def get_price_for_trade_requirement(self):
      if self.validities is None:
        return 0

      validity = self.validities[-1]


      result = common.get_money_exchange_for_fcl({"price":validity['price'], "from_currency":validity['currency'], "to_currency":'INR'})
      return result.get('price')
    
    def create_fcl_freight_free_days(self, origin_local, destination_local, performed_by_id, sourced_by_id, procured_by_id):
      obj = {}
      obj['specificity_type'] = 'rate_specific'
      obj['previous_days_applicable'] = False
      obj['performed_by_id'] = performed_by_id
      obj['sourced_by_id'] = sourced_by_id
      obj['procured_by_id'] = procured_by_id
      obj['container_size'] = self.container_size
      obj['container_type'] = self.container_type
      obj['shipping_line_id'] = self.shipping_line_id
      obj['service_provider_id'] = self.service_provider_id

      origin_detention_id = origin_demurrage_id = destination_detention_id = destination_demurrage_id = None

      if 'detention' in origin_local and origin_local['detention']:
          obj['location_id'] = self.origin_port_id
          obj['free_days_type'] = 'detention'
          obj['trade_type'] = 'export'
          obj.update(origin_local['detention'])
          origin_detention_id = FclFreightRateFreeDay.create(**obj).id

      if 'demurrage' in origin_local and origin_local['demurrage']:
          obj['location_id'] = self.origin_port_id
          obj['free_days_type'] = 'demurrage'
          obj['trade_type'] = 'export'
          obj.update(origin_local['demurrage'])
          origin_demurrage_id = FclFreightRateFreeDay.create(**obj).id

      if 'detention' in destination_local and destination_local['detention']:
          obj['location_id'] = self.destination_port_id
          obj['free_days_type'] = 'detention'
          obj['trade_type'] = 'import'
          obj.update(destination_local['detention'])
          destination_detention_id = FclFreightRateFreeDay.create(**obj).id

      if 'demurrage' in destination_local and destination_local['demurrage']:
          obj['location_id'] = self.destination_port_id
          obj['free_days_type'] = 'demurrage'
          obj['trade_type'] = 'import'
          obj.update(destination_local['demurrage'])
          destination_demurrage_id = FclFreightRateFreeDay.create(**obj).id

      self.origin_detention_id = origin_detention_id
      self.origin_demurrage_id = origin_demurrage_id
      self.destination_detention_id = destination_detention_id
      self.destination_demurrage_id = destination_demurrage_id
      self.save()

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