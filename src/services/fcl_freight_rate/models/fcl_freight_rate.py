from peewee import *
import datetime
from database.db_session import db
from playhouse.postgres_ext import *
from fastapi import HTTPException
from params import LineItem
import concurrent.futures
from fastapi.encoders import jsonable_encoder
from services.fcl_freight_rate.models.fcl_freight_rate_local import FclFreightRateLocal
from configs.fcl_freight_rate_constants import *
from schema import Schema, Optional
from configs.definitions import FCL_FREIGHT_CHARGES,FCL_FREIGHT_LOCAL_CHARGES,FCL_FREIGHT_CURRENCIES
from services.fcl_freight_rate.models.fcl_freight_rate_local_data import FclFreightRateLocalData
from services.fcl_freight_rate.models.fcl_freight_rate_free_day import FclFreightRateFreeDay
from configs.global_constants import DEFAULT_EXPORT_DESTINATION_DETENTION, DEFAULT_IMPORT_DESTINATION_DETENTION
from services.fcl_freight_rate.interaction.update_fcl_freight_rate_platform_prices import update_fcl_freight_rate_platform_prices
from configs.global_constants import HAZ_CLASSES
from micro_services.client import *
from configs.fcl_freight_rate_constants import DEFAULT_SCHEDULE_TYPES, DEFAULT_PAYMENT_TERM, DEFAULT_RATE_TYPE
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
    destination_local_id = UUIDField(index=True, null=True)
    destination_detention_id = UUIDField(index=True, null=True)
    destination_demurrage_id = UUIDField(index=True, null=True)
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
    origin_local_id = UUIDField(index=True, null=True)
    origin_detention_id = UUIDField(index=True, null=True)
    origin_demurrage_id = UUIDField(index=True, null=True)
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
    service_provider_id = UUIDField(index=True)
    service_provider = BinaryJSONField(null=True)
    shipping_line = BinaryJSONField(null=True)
    shipping_line_id = UUIDField(index=True)
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
    init_key = TextField(index=True, null=True)
    rate_type = CharField(default='market_place', choices = RATE_TYPES)
    tags = BinaryJSONField(null=True)
    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(FclFreightRate, self).save(*args, **kwargs)

    class Meta:
        table_name = 'fcl_freight_rates_temp'



    def set_locations(self):

      ids = [str(self.origin_port_id), str(self.destination_port_id)]
      if self.origin_main_port_id:
        ids.append(str(self.origin_main_port_id))
      if self.destination_main_port_id:
        ids.append(str(self.destination_main_port_id))

      obj = {'filters':{"id": ids, "type":'seaport'}}
      locations_response = maps.list_locations(obj)
      locations = []
      if 'list' in locations_response:
        locations = locations_response["list"]


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
        if self.origin_port and self.origin_port['is_icd'] and not self.rate_not_available_entry:
          if not self.origin_main_port_id or not self.origin_main_port or self.origin_main_port['is_icd']:
              return False

        return True


    def validate_destination_main_port_id(self):
        if self.destination_port and self.destination_port['is_icd'] and not self.rate_not_available_entry:
          if not self.destination_main_port_id or not self.destination_main_port or self.destination_main_port['is_icd']:
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

      free_days_query = FclFreightRateFreeDay.select().where(
        FclFreightRateFreeDay.container_size == self.container_size,
        FclFreightRateFreeDay.container_type == self.container_type,
        FclFreightRateFreeDay.location_id << [self.origin_port_id, self.destination_port_id],
        FclFreightRateFreeDay.service_provider_id == self.service_provider_id,
        FclFreightRateFreeDay.specificity_type == 'rate_specific'
      )
      if self.importer_exporter_id:
        free_days_query = free_days_query.where(FclFreightRateFreeDay.importer_exporter_id == self.importer_exporter_id)
      else:
        free_days_query = free_days_query.where(FclFreightRateFreeDay.importer_exporter_id == None)

      free_days = jsonable_encoder(list(free_days_query.dicts()))

      self.update_origin_free_days_special_attributes(free_days)
      self.update_destination_free_days_special_attributes(free_days)
      self.update_weight_limit_special_attributes()

    def update_origin_local_line_item_messages(self):

      response = {}

      if self.origin_local:
        self.origin_local_data_instance = FclFreightRateLocalData(self.origin_local)
        response = self.origin_local_data_instance.get_line_item_messages(self.origin_port,self.origin_main_port,self.shipping_line,self.container_size,self.container_type,self.commodity,'export',self.possible_origin_local_charge_codes())

      self.origin_local_line_items_error_messages = response.get('line_items_error_messages')
      self.is_origin_local_line_items_error_messages_present = response.get('is_line_items_error_messages_present')
      self.origin_local_line_items_info_messages = response.get('line_items_info_messages')
      self.is_origin_local_line_items_info_messages_present = response.get('is_line_items_info_messages_present')

    def update_destination_local_line_item_messages(self):
      response = {}
      if self.destination_local:
        self.destination_local_data_instance = FclFreightRateLocalData(self.destination_local)
        response = self.destination_local_data_instance.get_line_item_messages(self.destination_port,self.destination_main_port,self.shipping_line,self.container_size,self.container_type,self.commodity,'export',self.possible_origin_local_charge_codes())

      self.destination_local_line_items_error_messages = response.get('line_items_error_messages')
      self.is_destination_local_line_items_error_messages_present = response.get('is_line_items_error_messages_present')
      self.destination_local_line_items_info_messages = response.get('line_items_info_messages')
      self.is_destination_local_line_items_info_messages_present = response.get('is_line_items_info_messages_present')


    def update_origin_free_days_special_attributes(self, free_days):
      origin_detention = {}
      origin_demurrage = {}
      origin_plugin = {}
      for free_day_obj in free_days:
        if free_day_obj['trade_type'] == 'export' and free_day_obj['free_days_type'] == 'detention':
          origin_detention = free_day_obj
        if free_day_obj['trade_type'] == 'export' and free_day_obj['free_days_type'] == 'demurrage':
          origin_demurrage = free_day_obj
        if free_day_obj['trade_type'] == 'export' and free_day_obj['free_days_type'] == 'plugin':
          origin_plugin = free_day_obj
      self.is_origin_detention_slabs_missing = False
      self.is_origin_demurrage_slabs_missing = False
      self.is_origin_plugin_slabs_missing = False

      if not 'slabs' in origin_detention or len(origin_detention['slabs'] or []) == 0:
        self.is_origin_detention_slabs_missing = True
      if not 'slabs' in origin_demurrage or len(origin_demurrage['slabs'] or []) == 0:
        self.is_origin_demurrage_slabs_missing = True
      if not 'slabs' in origin_plugin or len(origin_plugin['slabs'] or []) == 0:
        self.is_origin_plugin_slabs_missing = True



    def update_destination_free_days_special_attributes(self, free_days):
      destination_detention = {}
      destination_demurrage = {}
      destination_plugin = {}
      for free_day_obj in free_days:
        if free_day_obj['trade_type'] == 'import' and free_day_obj['free_days_type'] == 'detention':
          destination_detention = free_day_obj
        if free_day_obj['trade_type'] == 'import' and free_day_obj['free_days_type'] == 'demurrage':
          destination_demurrage = free_day_obj
        if free_day_obj['trade_type'] == 'import' and free_day_obj['free_days_type'] == 'plugin':
          destination_plugin = free_day_obj
      self.is_destination_detention_slabs_missing = False
      self.is_destination_demurrage_slabs_missing = False
      self.is_destination_plugin_slabs_missing = False

      if not 'slabs' in destination_detention or len(destination_detention['slabs'] or []) == 0:
        self.is_destination_detention_slabs_missing = True
      if not 'slabs' in destination_demurrage or len(destination_demurrage['slabs'] or []) == 0:
        self.is_destination_demurrage_slabs_missing = True
      if not 'slabs' in destination_plugin or len(destination_plugin['slabs'] or []) == 0:
        self.is_destination_plugin_slabs_missing = True



    def update_weight_limit_special_attributes(self):
      if self.weight_limit:
        self.is_weight_limit_slabs_missing = (len(self.weight_limit.get('slabs',[])) == 0)
      else:
        self.is_weight_limit_slabs_missing = True

    def validate_origin_local(self):
      if 'origin_local' in self.dirty_fields and self.origin_local:
        if not self.origin_local_instance.validate_duplicate_charge_codes():
            raise HTTPException(status_code=400,detail="Duplicate line items in Origin Local")
        invalid_charge_codes = self.origin_local_instance.validate_invalid_charge_codes(self.possible_origin_local_charge_codes())
        if invalid_charge_codes:
            raise HTTPException(status_code=400,detail=f"{invalid_charge_codes} are invalid Origin Local line items")


    def validate_destination_local(self):
      if 'destination_local' in self.dirty_fields and self.destination_local:
        if not self.destination_local_instance.validate_duplicate_charge_codes():
            raise HTTPException(status_code=400,detail="Duplicate line items in Destination Local")
        invalid_charge_codes = self.destination_local_instance.validate_invalid_charge_codes(self.possible_destination_local_charge_codes())
        if invalid_charge_codes:
            raise HTTPException(status_code=400,detail=f"{invalid_charge_codes} are invalid Destination Local line items")

    def validate_validity_object(self, validity_start, validity_end):
      if not validity_start:
        raise HTTPException(status_code=400, detail="validity_start is invalid")

      if not validity_end:
        raise HTTPException(status_code=400, detail="validity_end is invalid")

      if validity_end.date() > (datetime.datetime.now().date() + datetime.timedelta(days=60)):
        raise HTTPException(status_code=400, detail="validity_end can not be greater than 60 days from current date")

      if validity_end.date() < (datetime.datetime.now().date() + datetime.timedelta(days=2)):
        raise HTTPException(status_code=400, detail="validity_end can not be less than 2 days from current date")

      if validity_start.date() < (datetime.datetime.now().date() - datetime.timedelta(days=15)):
        raise HTTPException(status_code=400, detail="validity_start can not be less than 15 days from current date")

      if validity_end < validity_start:
        raise HTTPException(status_code=400, detail="validity_end can not be lesser than validity_start")

    def validate_line_items(self, line_items):
      if(line_items==None or len(line_items)==0):
        raise HTTPException(status_code=400, detail="line_items required")

      codes = [item['code'] for item in line_items]
      if len(set(codes)) != len(codes) and (self.rate_type != "cogo_assured"):
        raise HTTPException(status_code=400, detail="line_items contains duplicates")


      fcl_freight_charges_dict = FCL_FREIGHT_CHARGES

      invalid_line_items = [code for code in codes if code not in fcl_freight_charges_dict.keys()]

      if invalid_line_items:
          raise HTTPException(status_code=400, detail="line_items {} are invalid".format(", ".join(invalid_line_items)))

      fcl_freight_currencies = FCL_FREIGHT_CURRENCIES

      currencies = [currency for currency in fcl_freight_currencies]
      line_item_currencies = [item['currency'] for item in line_items]

      if any(currency not in currencies for currency in line_item_currencies):
        raise HTTPException(status_code=400, detail='line_item_currency is invalid')

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
          raise HTTPException(status_code=400, detail="line_items does not contain all mandatory_codes {}".format(", ".join([code for code in mandatory_codes if code not in codes])))

    def get_platform_price(self, validity_start, validity_end, price, currency, rate_type):
      freight_rates = FclFreightRate.select(FclFreightRate.validities, FclFreightRate.id).where(
            (FclFreightRate.origin_port_id == self.origin_port_id) &
            (FclFreightRate.origin_main_port_id == self.origin_main_port_id) &
            (FclFreightRate.destination_port_id == self.destination_port_id) &
            (FclFreightRate.destination_main_port_id == self.destination_main_port_id) &
            (FclFreightRate.container_size == self.container_size) &
            (FclFreightRate.container_type == self.container_type) &
            (FclFreightRate.commodity == self.commodity) &
            (FclFreightRate.shipping_line_id == self.shipping_line_id) &
            (FclFreightRate.service_provider_id != self.service_provider_id) &
            (FclFreightRate.rate_type == rate_type)
            ).where(FclFreightRate.importer_exporter_id.in_([None, self.importer_exporter_id])).execute()

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

    def set_platform_prices(self, rate_type=DEFAULT_RATE_TYPE):
      with concurrent.futures.ThreadPoolExecutor(max_workers = 4) as executor:
        futures = [executor.submit(self.get_platform_price,validity_object['validity_start'], validity_object['validity_end'], validity_object['price'], validity_object['currency'], rate_type ) for validity_object in self.validities]
        for i in range(0,len(futures)):
          self.validities[i]['platform_price'] = futures[i].result()

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

    def set_validities_for_cogo_assured_rates(self,validities):
      new_validities = []
      for validity in validities:
        validity['id'] = str(uuid.uuid4())
        validity["schedule_type"] =  DEFAULT_SCHEDULE_TYPES
        validity["payment_term"] =  DEFAULT_PAYMENT_TERM
        validity["likes_count"] = 0
        validity["dislikes_count"] = 0

        new_validities.append(FclFreightRateValidity(**validity))

      new_validities = [validity for validity in new_validities if datetime.datetime.strptime(str(validity.validity_end).split('T')[0], '%Y-%m-%d').date() >= datetime.datetime.now().date()]
      new_validities = sorted(new_validities, key=lambda validity: datetime.datetime.strptime(str(validity.validity_start).split('T')[0], '%Y-%m-%d').date())
      
      main_validities=[]
      for new_validity in new_validities:
        new_validity.line_items = [dict(line_item) for line_item in new_validity.line_items]
        new_validity.validity_start = datetime.datetime.strptime(str(new_validity.validity_start).split('T')[0], '%Y-%m-%d').date().isoformat()
        new_validity.validity_end = datetime.datetime.strptime(str(new_validity.validity_end).split('T')[0], '%Y-%m-%d').date().isoformat()
        new_validity = vars(new_validity)
        new_validity['id'] = new_validity['__data__']['id']
        new_validity.pop('__data__')
        new_validity.pop('__rel__')
        new_validity.pop('_dirty')
        main_validities.append(new_validity)
      self.validities = main_validities


    def set_validities(self, validity_start, validity_end, line_items, schedule_type, deleted, payment_term):
        new_validities = []
        if not schedule_type:
          schedule_type = DEFAULT_SCHEDULE_TYPES
        if not payment_term:
          payment_term = DEFAULT_PAYMENT_TERM

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
                # validity_object_validity_end = validity_start - datetime.timedelta(days=1)
                validity_object['validity_end'] = validity_start - datetime.timedelta(days=1)
                new_validities.append(FclFreightRateValidity(**validity_object))
                continue
            if validity_object_validity_start >= validity_start and validity_object_validity_end > validity_end:
                # validity_object_validity_start = validity_end + datetime.timedelta(days=1)
                validity_object['validity_start'] = validity_end + datetime.timedelta(days=1)
                new_validities.append(FclFreightRateValidity(**validity_object))
                continue
            if validity_object_validity_start < validity_start and validity_object_validity_end > validity_end:
                new_validities.append(FclFreightRateValidity(**{**validity_object, 'validity_end': validity_start - datetime.timedelta(days=1)}))
                new_validities.append(FclFreightRateValidity(**{**validity_object, 'validity_start': validity_end + datetime.timedelta(days=1)}))
                continue

        new_validities = [validity for validity in new_validities if datetime.datetime.strptime(str(validity.validity_end).split(' ')[0], '%Y-%m-%d').date() >= datetime.datetime.now().date()]
        new_validities = sorted(new_validities, key=lambda validity: datetime.datetime.strptime(str(validity.validity_start).split(' ')[0], '%Y-%m-%d').date())

        main_validities=[]
        for new_validity in new_validities:
          new_validity.line_items = [dict(line_item) for line_item in new_validity.line_items]
          new_validity.validity_start = datetime.datetime.strptime(str(new_validity.validity_start).split(' ')[0], '%Y-%m-%d').date().isoformat()
          new_validity.validity_end = datetime.datetime.strptime(str(new_validity.validity_end).split(' ')[0], '%Y-%m-%d').date().isoformat()
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
          raise HTTPException(status_code=400, detail="slabs lower limit should be greater than free limit")

        for index, weight_limit_slab in enumerate(self.weight_limit['slabs']):
          if (weight_limit_slab['upper_limit'] <= weight_limit_slab['lower_limit']) or (index != 0 and weight_limit_slab['lower_limit'] <= self.weight_limit['slabs'][index - 1]['upper_limit']):
            raise HTTPException(status_code=400, detail="slabs are not valid")

      self.origin_local_instance = FclFreightRateLocalData(self.origin_local)
      self.destination_local_instance = FclFreightRateLocalData(self.destination_local)

      if not self.validate_container_size():
        raise HTTPException(status_code=400, detail="incorrect container size")
      if not self.validate_container_type():
        raise HTTPException(status_code=400, detail="incorrect container type")
      if not self.validate_commodity():
        raise HTTPException(status_code=400, detail="incorrect commodity")

      self.set_omp_dmp_sl_sp()
      self.validate_origin_local()
      self.validate_destination_local()

      if not self.validate_origin_main_port_id():
        raise HTTPException(status_code=400, detail="origin main port id is required")

      if not self.validate_destination_main_port_id():
        raise HTTPException(status_code=400, detail="destination main port id is required")

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
      commodity = self.commodity if self.commodity in HAZ_CLASSES else None
      local_objects_query = FclFreightRateLocal.select().where(
        FclFreightRateLocal.port_id << (self.origin_port_id, self.destination_port_id),
        FclFreightRateLocal.container_size == self.container_size,
        FclFreightRateLocal.container_type == self.container_type,
        FclFreightRateLocal.commodity == commodity,
        FclFreightRateLocal.service_provider_id == self.service_provider_id,
        FclFreightRateLocal.shipping_line_id == self.shipping_line_id
      )

      main_port_ids = []
      if self.origin_main_port_id:
        main_port_ids.append(str(self.origin_main_port_id))
      if self.destination_main_port_id:
        main_port_ids.append(str(self.destination_main_port_id))

      if len(main_port_ids) == 2:
        local_objects_query = local_objects_query.where(FclFreightRateLocal.main_port_id << main_port_ids)
      elif len(main_port_ids) == 1:
        local_objects_query = local_objects_query.where((FclFreightRateLocal.main_port_id.is_null(True) | FclFreightRateLocal.main_port_id << main_port_ids))

      local_objects = jsonable_encoder(list(local_objects_query.dicts()))

      origin_locals = []
      destination_locals = []

      for local in local_objects:
        if local['port_id'] == self.origin_port_id and (not self.origin_main_port_id or self.origin_main_port_id == local['main_port_id']) and local['trade_type'] == 'export':
          origin_locals.append(local)
        if local['port_id'] == self.destination_port_id and (not self.destination_main_port_id or self.destination_main_port_id == local['main_port_id']) and local['trade_type'] == 'import':
          destination_locals.append(local)

      origin_local_object_id = origin_locals[0]["id"] if len(origin_locals) > 0 else None
      destination_local_object_id = destination_locals[0]["id"] if len(destination_locals) > 0 else None

      self.origin_local_id = origin_local_object_id
      self.destination_local_id = destination_local_object_id

    def detail(self):
      data = {
          'freight': {
              'id': self.id,
              'validities': self.validities,
              'is_best_price': self.is_best_price,
              'is_rate_expired': self.is_rate_expired(),
              'is_rate_about_to_expire': self.is_rate_about_to_expire(),
              'is_rate_not_available': self.is_rate_not_available(),
              # 'origin_port_id': self.origin_port_id,
              # 'origin_main_port_id': self.origin_main_port_id,
              # 'destination_port_id': self.destination_port_id,
              # 'destination_main_port_id': self.destination_main_port_id,
              # 'service_provider_id': self.service_provider_id,
              # 'shipping_line_id': self.shipping_line_id,

          },
          'weight_limit': dict(self.weight_limit or {})
        }

      data = {k: v for k, v in data.items()}

      origin_local = self.origin_local
      destination_local = self.destination_local

      local_ids = []
      if self.origin_local_id:
        local_ids.append(str(self.origin_local_id))
      if self.destination_local_id:
        local_ids.append(str(self.destination_local_id))

      free_day_ids = []

      if self.origin_detention_id:
        free_day_ids.append(str(self.origin_detention_id))
      if self.origin_demurrage_id:
        free_day_ids.append(str(self.origin_demurrage_id))
      if self.origin_plugin_id:
        free_day_ids.append(str(self.origin_plugin_id))

      if self.destination_detention_id:
        free_day_ids.append(str(self.destination_detention_id))
      if self.destination_demurrage_id:
        free_day_ids.append(str(self.destination_demurrage_id))
      if self.destination_plugin_id:
        free_day_ids.append(str(self.destination_plugin_id))

      local_charges = {}

      if len(local_ids):
        local_charges_query = FclFreightRateLocal.select(
          FclFreightRateLocal.id,
          FclFreightRateLocal.port_id,
          FclFreightRateLocal.line_items,
          FclFreightRateLocal.data,
          FclFreightRateLocal.is_line_items_error_messages_present,
          FclFreightRateLocal.line_items_error_messages,
          FclFreightRateLocal.is_line_items_info_messages_present,
          FclFreightRateLocal.line_items_info_messages,
          FclFreightRateLocal.trade_type
        ).where(FclFreightRateLocal.id << local_ids, (~FclFreightRateLocal.rate_not_available_entry | FclFreightRateLocal.rate_not_available_entry.is_null(True)))

        local_charges_new = jsonable_encoder(list(local_charges_query.dicts()))

        for local_charge in local_charges_new:
          local_charges[local_charge["id"]] = local_charge

      free_days_charges = {}

      if len(free_day_ids):
        free_days_query = FclFreightRateFreeDay.select(
          FclFreightRateFreeDay.location_id,
          FclFreightRateFreeDay.id,
          FclFreightRateFreeDay.slabs,
          FclFreightRateFreeDay.free_days_type,
          FclFreightRateFreeDay.specificity_type,
          FclFreightRateFreeDay.is_slabs_missing
        ).where(FclFreightRateFreeDay.id << free_day_ids, (~FclFreightRateFreeDay.rate_not_available_entry | FclFreightRateFreeDay.rate_not_available_entry.is_null(True)))
        free_days_new = jsonable_encoder(list(free_days_query.dicts()))

        for free_day_charge in free_days_new:
          free_day_charge[free_day_charge["id"]] = free_day_charge


      if self.origin_local_id in local_charges and (not origin_local or not 'line_items' in origin_local or len(origin_local['line_items'] == 0)):
        origin_local = local_charges[self.origin_local_id]

      if self.origin_detention_id in free_days_charges:
        origin_local['detention'] = free_days_charges[self.origin_detention_id] | ({'is_slabs_missing': self.is_origin_detention_slabs_missing })
      else:
        origin_local['detention'] = { 'free_limit': DEFAULT_EXPORT_DESTINATION_DETENTION, 'is_slabs_missing': True, 'slabs': [] }

      if self.origin_demurrage_id in free_days_charges:
        origin_local['demurrage'] = free_days_charges[self.origin_demurrage_id] | ({'is_slabs_missing': self.is_origin_demurrage_slabs_missing })
      else:
        origin_local['demurrage'] = { 'free_limit': 0, 'is_slabs_missing': True, 'slabs': [] }

      if self.origin_plugin_id in free_days_charges:
        origin_local['plugin'] = free_days_charges[self.origin_plugin_id] | ({'is_slabs_missing': self.is_origin_plugin_slabs_missing })
      else:
        origin_local['plugin'] = { 'free_limit': 0, 'is_slabs_missing': True, 'slabs': [] }

      if self.destination_local_id in local_charges and (not destination_local or not 'line_items' in destination_local or len(destination_local['line_items'] == 0)):
        destination_local = local_charges[self.destination_local_id]

      if self.destination_detention_id in free_days_charges:
        destination_local['detention'] = free_days_charges[self.destination_detention_id] | ({'is_slabs_missing': self.is_destination_detention_slabs_missing })
      else:
        destination_local['detention'] = { 'free_limit': DEFAULT_IMPORT_DESTINATION_DETENTION, 'is_slabs_missing': True, 'slabs': [] }

      if self.destination_demurrage_id in free_days_charges:
        destination_local['demurrage'] = free_days_charges[self.destination_demurrage_id] | ({'is_slabs_missing': self.is_destination_demurrage_slabs_missing })
      else:
        destination_local['demurrage'] = { 'free_limit': 0, 'is_slabs_missing': True, 'slabs': [] }

      if self.destination_plugin_id in free_days_charges:
        destination_local['plugin'] = free_days_charges[self.destination_plugin_id] | ({'is_slabs_missing': self.is_destination_plugin_slabs_missing })
      else:
        destination_local['plugin'] = { 'free_limit': 0, 'is_slabs_missing': True, 'slabs': [] }
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
              "is_origin_local_missing": (not self.origin_local or not 'line_items' in self.origin_local or len(self.origin_local['line_items']) == 0),
              "is_destination_local_missing": (not self.destination_local or not 'line_items' in self.destination_local or len(self.destination_local['line_items']) == 0),
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

    def get_price_for_trade_requirement(self):
      if self.validities is None:
        return 0

      validity = self.validities[-1]


      result = common.get_money_exchange_for_fcl({"price":validity['price'], "from_currency":validity['currency'], "to_currency":'INR'})
      return result.get('price')

    def create_fcl_freight_free_days(self, new_free_days, performed_by_id, sourced_by_id, procured_by_id):
      from services.fcl_freight_rate.interaction.create_fcl_freight_rate_free_day import create_fcl_freight_rate_free_day
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

      if 'origin_detention' in  new_free_days and new_free_days['origin_detention']:
          obj['location_id'] = self.origin_port_id
          obj['free_days_type'] = 'detention'
          obj['trade_type'] = 'export'
          obj.update(new_free_days['origin_detention'])
          origin_detention_obj = create_fcl_freight_rate_free_day(obj)
          origin_detention_id = origin_detention_obj["id"]

      if 'origin_demurrage' in new_free_days and new_free_days['origin_demurrage']:
          obj['location_id'] = self.origin_port_id
          obj['free_days_type'] = 'demurrage'
          obj['trade_type'] = 'export'
          obj.update(new_free_days['origin_demurrage'])
          origin_demurrage_obj = create_fcl_freight_rate_free_day(obj)
          origin_demurrage_id = origin_demurrage_obj["id"]

      if 'destination_detention' in new_free_days and new_free_days['destination_detention']:
          obj['location_id'] = self.destination_port_id
          obj['free_days_type'] = 'detention'
          obj['trade_type'] = 'import'
          obj.update(new_free_days['destination_detention'])
          destination_detention_obj = create_fcl_freight_rate_free_day(obj)
          destination_detention_id = destination_detention_obj["id"]

      if 'destination_demurrage' in new_free_days and new_free_days['destination_demurrage']:
          obj['location_id'] = self.destination_port_id
          obj['free_days_type'] = 'demurrage'
          obj['trade_type'] = 'import'
          obj.update(new_free_days['destination_demurrage'])
          destination_demurrage_obj = create_fcl_freight_rate_free_day(obj)
          destination_demurrage_id = destination_demurrage_obj["id"]

      self.origin_detention_id = origin_detention_id
      self.origin_demurrage_id = origin_demurrage_id
      self.destination_detention_id = destination_detention_id
      self.destination_demurrage_id = destination_demurrage_id

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
