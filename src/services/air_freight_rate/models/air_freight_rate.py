from peewee import *
import datetime
from database.db_session import db
from fastapi import HTTPException
from configs.air_freight_rate_constants import *
from playhouse.postgres_ext import *
from micro_services.client import *
from database.rails_db import *
from fastapi.encoders import jsonable_encoder
from services.air_freight_rate.models.air_freight_rate_local import AirFreightRateLocal
from services.air_freight_rate.models.air_freight_rate_surcharge import AirFreightRateSurcharge
from configs.global_constants import *
from configs.definitions import AIR_FREIGHT_CHARGES
from air_freight_rate_params import WeightSlab
class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class AirFreightRate(BaseModel):
    airline = BinaryJSONField(null=True)
    airline_id = UUIDField(null=True, index=True)
    breadth = IntegerField(null=True)
    commodity = CharField(null=True, index=True)
    commodity_sub_type = CharField(null=True)
    commodity_type = CharField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now, index=True,null=True)
    currency = CharField(null=True)
    destination_airport = BinaryJSONField(null=True)
    destination_airport_id = UUIDField(index=True,null=True)
    destination_continent_id = UUIDField(null=True)
    destination_country_id = UUIDField(null=True)
    destination_local = BinaryJSONField(null=True)
    destination_local_id = UUIDField(null=True)
    destination_location_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, index=True, null=True)
    destination_local_line_items_error_messages = BinaryJSONField(constraints=[SQL("DEFAULT '{}'::jsonb")], null=True)
    destination_local_line_items_info_messages = BinaryJSONField(constraints=[SQL("DEFAULT '{}'::jsonb")], null=True)
    destination_storage_id = UUIDField(null=True)
    destination_trade_id = UUIDField(null=True)
    discount_type = CharField(null=True)
    external_rate_id=UUIDField(null=True)
    flight_uuid = UUIDField(null=True)
    height = IntegerField(null=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    importer_exporter = BinaryJSONField(null=True)
    importer_exporter_id = UUIDField(null=True)
    is_best_price = BooleanField(null=True)
    is_destination_local_line_items_error_messages_present = BooleanField(null=True)
    is_destination_local_line_items_info_messages_present = BooleanField(null=True)
    is_origin_local_line_items_error_messages_present = BooleanField(null=True)
    is_origin_local_line_items_info_messages_present = BooleanField(null=True)
    last_rate_available_date = DateTimeField(index=True, null=True)
    length = IntegerField(null=True)
    maximum_weight = IntegerField(null=True)
    min_price = FloatField(null=True)
    operation_type = CharField(index=True, null=True)
    origin_airport = BinaryJSONField(null=True)
    origin_airport_id = UUIDField(null=True, index=True)
    origin_continent_id = UUIDField(null=True)
    origin_country_id = UUIDField(null=True)
    origin_local = BinaryJSONField(null=True)
    origin_local_id = UUIDField(null=True)
    origin_location_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, index=True, null=True)
    origin_local_line_items_error_messages = BinaryJSONField(constraints=[SQL("DEFAULT '{}'::jsonb")], null=True)
    origin_local_line_items_info_messages = BinaryJSONField(constraints=[SQL("DEFAULT '{}'::jsonb")], null=True)
    origin_storage_id = UUIDField(null=True)
    origin_trade_id = UUIDField(null=True)
    price_type = CharField(null=True)
    rate_not_available_entry = BooleanField(constraints=[SQL("DEFAULT false")], null=True)
    rate_type = CharField(default='market_place' ,choices = RATE_TYPES)
    service_provider = BinaryJSONField(null=True)
    service_provider_id = UUIDField(null=True)
    shipment_type = CharField(null=True)
    stacking_type = CharField(null=True)
    surcharge = BinaryJSONField(null=True)
    surcharge_id = UUIDField(null=True)
    updated_at = DateTimeField(default=datetime.datetime.now, index=True)
    validities = BinaryJSONField(default = [], null=True)
    warehouse_rate_id = UUIDField(null=True)
    weight_slabs = BinaryJSONField(null=True)
    mode = CharField(default = 'manual', null = True)
    accuracy = FloatField(default = 100, null = True)
    cogo_entity_id = UUIDField(index=True, null=True)
    sourced_by_id = UUIDField(null=True, index=True)
    procured_by_id = UUIDField(null=True, index=True)
    sourced_by = BinaryJSONField(null=True)
    procured_by = BinaryJSONField(null=True)
    init_key = TextField(index=True, null=True)
    is_surcharge_line_items_error_messages_present = BooleanField(null=True)
    is_surcharge_line_items_info_messages_present = BooleanField(null=True)
    surcharge_line_items_error_messages = BinaryJSONField(constraints=[SQL("DEFAULT '{}'::jsonb")], null=True)
    surcharge_line_items_info_messages = BinaryJSONField(constraints=[SQL("DEFAULT '{}'::jsonb")], null=True)

    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(AirFreightRate, self).save(*args, **kwargs)
    
    class Meta:
        table_name = 'air_freight_rates_temp1'


<<<<<<< HEAD
    def validate_validity_object(self,validity_start,validity_end):
        
=======
    def validate_validity_object(self, validity_start, validity_end):

>>>>>>> d517885202f393fa52033b7a6210df71f9fc5322
        if not validity_start:
            raise HTTPException(status_code=400,details='Validity Start is Invalid')
    
        if not validity_end:
            raise HTTPException(status_code=400, detail="validity_end is Invalid")

        if validity_end.date() > (datetime.datetime.now().date() + datetime.timedelta(days=120)):
            raise HTTPException(status_code=400, detail="validity_end can not be greater than 120 days from current date")

        if validity_start.date() < (datetime.datetime.now().date() - datetime.timedelta(days=15)):
            raise HTTPException(status_code=400, detail="validity_start can not be less than 15 days from current date")

        if validity_end <= validity_start:
            raise HTTPException(status_code=400, detail="validity_end can not be lesser than validity_start")
        

    def validate_shipment_type(self):
        if self.shipment_type not in PACKING_TYPE:
            raise HTTPException(status_code=400,details = 'Invalid Shipment Type')
        
    def validate_stacking_type(self):
        if self.stacking_type not in HANDLING_TYPE:
            raise HTTPException(status_code=400,details = 'Invalid Stacking Type')
    
    def validate_commodity(self):
        if self.commodity not in COMMODITY:
            raise HTTPException(status_code=400,details = 'Invalid Commodity')

    def validate_commodity_type(self):
        if self.commodity_type not in COMMODITY_TYPE:
            raise HTTPException(status_code=400,details = 'Invalid Commodity Type')
    
    def validate_commodity_sub_type(self):
        if self.commodity_sub_type not in COMMODITY_SUB_TYPE:
            raise HTTPException(status_code=400,details = 'Invalid Commodity Sub Type')
    
    def validate_price_type(self):
        if self.price_type not in PRICE_TYPES:
            raise HTTPException(status_code = 400,details = 'Invalid Price Type')
        
    def validations(self):
        self.validate_shipment_type()
        self.validate_stacking_type()
        self.validate_commodity()
        self.validate_commodity_type()
        self.validate_price_type()

        if self.length < 0:
            raise HTTPException(status_code = 400,details = 'Length Should Be Positive Value')
        
        if self.breadth < 0:
            raise HTTPException(status_code = 400,details = 'Bredth Should Be Positive Value')

        if self.height < 0:
            raise HTTPException(status_code = 400,details = 'Height Should Be Positive Value')
        
        if self.rate_type not in RATE_TYPES:
            raise HTTPException(status_code = 400,details = 'Invalid Rate Type')
        self.validate_available_volume_and_gross_weight()
        self.validate_origin_destination_country()
        self.validate_service_provider_id()
        self.validate_airline_id()
        return True
    
    def validate_available_volume_and_gross_weight(self):
        if self.commodity!='general':
            for validity in self.validities:
                if validity['available_volume'] > validity['initial_volume']:
                    raise HTTPException(status_code = 400,details='available volume can\'t be greater than initial volume')
                
                if validity['available_gross_weight'] > validity['initial_gross_weight']:
                    raise HTTPException(status_code = 400,details='available gross weight can\'t be greater than initial gross weight')
                
    def set_locations(self):

      ids = [str(self.origin_airport_id), str(self.destination_airport_id)]

      obj = {'filters':{"id": ids, "type":'seaport'}}
      locations_response = maps.list_locations(obj)
      locations = []
      if 'list' in locations_response:
        locations = locations_response["list"]


      for location in locations:
        if str(self.origin_airport_id) == str(location['id']):
          self.origin_airport = self.get_required_location_data(location)
        if str(self.destination_airport_id) == str(location['id']):
          self.destination_airport = self.get_required_location_data(location)


    def get_required_location_data(self, location):
        loc_data = {
          "id": location["id"],
          "name": location["name"],
          "is_icd": location["is_icd"],
          "airport_code": location["port_code"],
          "country_id": location["country_id"],
          "continent_id": location["continent_id"],
          "trade_id": location["trade_id"],
          "country_code": location["country_code"]
        }
        return loc_data

    def set_origin_location_ids(self):
      self.origin_country_id = self.origin_airport.get('country_id')
      self.origin_continent_id = self.origin_airport.get('continent_id')
      self.origin_trade_id = self.origin_airport.get('trade_id')
      self.origin_location_ids = [uuid.UUID(str(self.origin_airport_id)),uuid.UUID(str(self.origin_country_id)),uuid.UUID(str(self.origin_trade_id)),uuid.UUID(str(self.origin_continent_id))]

    def set_destination_location_ids(self):
      self.destination_country_id = self.destination_airport.get('country_id')
      self.destination_continent_id = self.destination_aorport.get('continent_id')
      self.destination_trade_id = self.destination_airport.get('trade_id')
      self.destination_location_ids = [uuid.UUID(str(self.destination_port_id)),uuid.UUID(str(self.destination_country_id)),uuid.UUID(str(self.destination_trade_id)),uuid.UUID(str(self.destination_continent_id))]

    def validate_origin_destination_country(self):
        if self.origin_airport['country_code'] == self.destination_airport['country_code']:
            raise HTTPException(status_code = 400, details = 'Destination Airport Cannot be in the Same Origin Country')

    def validate_service_provider_id(self):
        service_provider_data = get_organization(id=str(self.service_provider_id))
        if (len(service_provider_data) != 0) and service_provider_data[0].get('account_type') == 'service_provider':
            self.service_provider = service_provider_data[0]
            return True
        raise HTTPException(status_code = 400, details = 'Service Provider Id Is Not Valid') 
           
    def validate_airline_id(self):
        airline_data = get_shipping_line(id=self.airline_id,operator_type='airline')
        if (len(airline_data) != 0) and airline_data[0].get('operator_type') == 'shipping_line':
            self.airline = airline_data[0]
            return True
        raise HTTPException(status_code = 400, details = 'Airline Id Is Not Valid')    

    def validate_operation_type(self):
        if self.operation_type not in AIR_OPERATION_TYPES:
            raise HTTPException(status_code = 400, details = 'Invalid Operation Type')  

    def update_foreign_references(self):
        self.update_local_references()
        if self.price_type != 'all_in':
            self.update_surcharge_reference()
    
    def update_local_references(self):
        location_ids = [self.origin_airport_id,self.destination_airport_id]
        locals = AirFreightRateLocal.select().where(
            AirFreightRateLocal.airport_id << location_ids,
            AirFreightRateLocal.airline_id == self.airline_id,
            AirFreightRateLocal.commodity == self.commodity,
            AirFreightRateLocal.commodity_type == self.commodity_type,
            AirFreightRateLocal.service_provider_id == self.service_provider_id
        )
        
        locals= jsonable_encoder(list(locals.dicts()))


        origin_local_id = None
        destination_local_id = None

        for local in locals:
            if local['airport_id'] == self.origin_airport_id and local['trade_type'] == 'export':
                origin_local_id = local['id']
            
            if local['airport_id'] == self.destination_airport_id and local['trade_type'] == 'import':
                destination_local_id = local['id']
        
        self.origin_local_id = origin_local_id
        self.destination_local_id = destination_local_id
        self.save()
    
    def update_surcharge_reference(self):

        surcharge = AirFreightRateSurcharge.select(AirFreightRateSurcharge.id).where(
            AirFreightRateSurcharge.origin_airport_id == self.origin_airport_id,
            AirFreightRateSurcharge.destination_airport_id == self.destination_airport_id,
            AirFreightRateSurcharge.commodity == self.commodity,
            AirFreightRateSurcharge.commodity_type == self.commodity_type,
            AirFreightRateSurcharge.airline_id == self.airline_id,
            AirFreightRateSurcharge.service_provider_id == self.service_provider_id
        ).first()

        if surcharge:
            self.surcharge_id = surcharge.id 
    
    def detail(self):
        details =  {
            'freight':{
                'id':self.id,
                'validities':self.validities,
                'is_rate_expired':self.is_rate_expired(),
                'is_rate_about_to_expire': self.is_rate_about_to_expire(),
                'is_rate_not_available' : self.is_rate_not_available()
            }
        }

        location_ids = [self.origin_airport_id,self.destination_airport_id]
        locals = AirFreightRateLocal.select(AirFreightRateLocal.id,AirFreightRateLocal.line_items,
            AirFreightRateLocal.line_items_info_messages,AirFreightRateLocal.is_line_items_info_messages_present,
            AirFreightRateLocal.line_items_error_messages,AirFreightRateLocal.is_line_items_error_messages_present).where(
            AirFreightRateLocal.airport_id << location_ids,
            AirFreightRateLocal.airline_id == self.airline_id,
            AirFreightRateLocal.commodity == self.commodity,
            AirFreightRateLocal.commodity_type == self.commodity_type,
            AirFreightRateLocal.service_provider_id == self.service_provider_id
        )
        
        locals= jsonable_encoder(list(locals.dicts()))


        origin_local = None
        destination_local = None

        for local in locals:
            if local['airport_id'] == self.origin_airport_id and local['trade_type'] == 'export':
                origin_local = local
            
            if local['airport_id'] == self.destination_airport_id and local['trade_type'] == 'import':
                destination_local = local
        
        surcharge = AirFreightRateSurcharge.select(AirFreightRateSurcharge.id,AirFreightRateSurcharge.line_items,
            AirFreightRateSurcharge.line_items_info_messages,AirFreightRateSurcharge.is_line_items_info_messages_present,
            AirFreightRateSurcharge.line_items_error_messages,AirFreightRateSurcharge.is_line_items_error_messages_present).where(
            AirFreightRateSurcharge.origin_airport_id == self.origin_airport_id,
            AirFreightRateSurcharge.destination_airport_id == self.destination_airport_id,
            AirFreightRateSurcharge.commodity == self.commodity,
            AirFreightRateSurcharge.commodity_type == self.commodity_type,
            AirFreightRateSurcharge.airline_id == self.airline_id,
            AirFreightRateSurcharge.service_provider_id == self.service_provider_id
        )
        surcharge = jsonable_encoder(list(surcharge.dicts()))
        details['origin_local'] = origin_local
        details['destination_local'] = destination_local
        details['surcharge'] = surcharge[0]

        return details
          
    def is_rate_expired(self):
        if not self.last_rate_available_date:
            return
        return self.last_rate_available_date < datetime.datetime.now()
    
    def is_rate_about_to_expire(self):
        if not self.last_rate_available_date:
            return
        return self.last_rate_available_date <=  datetime.datetime.now() + datetime.timedelta(days=SEARCH_START_DATE_OFFSET)
    
    def is_rate_not_available(self):
        return not self.last_rate_available_date

    def possible_charge_codes(self):
      air_freight_charges = AIR_FREIGHT_CHARGES

      charge_codes = {}
      commodity = self.commodity
      commodity_type = self.commodity_type
      commodity_sub_type = self.commodity_sub_type

      for k,v in air_freight_charges.items():
          if eval(str(v['condition'])):
              charge_codes[k] = v
      return charge_codes
    
    def set_last_rate_available_date(self):
        new_validities = []
        if self.validities is not None:
            for validity in self.validities:
                if validity['status']:
                    new_validities.append(validity)
        
        if new_validities:
            self.last_rate_available_date = new_validities[-1]['validity_end']
    

    def create_trade_requirement_rate_mapping(self, procured_by_id, performed_by_id):
      return # todo check if we need to develop autoquotation
      if not self.last_rate_available_date:
          return
      data={
              "rate_id": self.id,
              "service": "air_freight",
              "performed_by_id": performed_by_id,
              "procured_by_id": procured_by_id,
              "last_updated_at": self.updated_at.replace(microsecond=0).isoformat(),
              "last_rate_available_date": datetime.datetime.strptime(str(self.last_rate_available_date), '%Y-%m-%d').date().isoformat(),
              "price": self.get_price_for_trade_requirement(),
              "price_currency": "INR",
              "is_origin_local_missing": (not self.origin_local or not 'line_items' in self.origin_local or len(self.origin_local['line_items']) == 0),
              "is_destination_local_missing": (not self.destination_local or not 'line_items' in self.destination_local or len(self.destination_local['line_items']) == 0),
              "rate_params": {
                  "origin_location_id": self.origin_airport_id,
                  "destination_location_id": self.destinationair_port_id,
                  "commodity": self.commodity,
                  "operation_type": self.operation_type

              }
          }
      # common.create_organization_trade_requirement_rate_mapping(data)


    def get_price_for_trade_requirement(self):
      
      if self.validities is None:
        return 0

      validity = self.validities[-1]

      weight_slab  = validity.get('weight_slabs')[0]
      price = weight_slab.get('tariff_price')
      currency = weight_slab.get('currency')

      result = common.get_money_exchange_for_fcl({"price":price, "from_currency":currency, "to_currency":'INR'})
      return result.get('price')
    
    def set_validities(self,validity_start, validity_end, min_price, currency, weight_slabs, deleted, validity_id, density_category, density_ratio, initial_volume, initial_gross_weight, available_volume, available_gross_weight, rate_type):
        new_validities = []
        min_density_weight = 0.01  
        max_density_weight = MAX_CARGO_LIMIT
        new_weight_slabs = weight_slabs

        if density_category =='low_density':
            if density_ratio:
                min_density_weight=float(density_ratio.replace(' ', '').split(':')[-1])
                max_density_weight=min_density_weight
        elif density_category=="high_density":
            if density_ratio:
                min_density_weight=float(density_ratio.replace(' ','').split(':')[-1])
                max_density_weight=MAX_CARGO_LIMIT
        if self.validities is not None:   
            for validity_object in self.validities:
                if not validity_object.get("density_category"):
                    validity_object['density_category'] = 'general'

                if validity_object.get('status') ==False:
                    new_validities.append(validity_object)
                    continue
                if validity_object.get("density_category") == 'high_density'  and  not deleted and  validity_object.get("density_category") == density_category:
                    if validity_object.get('min_density_weight') < min_density_weight and validity_object.get('max_density_weight') > min_density_weight:
                        validity_object['max_density_weight'] = min_density_weight
                    if validity_object.get('min_density_weight') > min_density_weight and max_density_weight > validity_object.get('min_density_weight'):
                        max_density_weight = validity_object.get('min_density_weight')

                if validity_object.get('density_category') == density_category and max_density_weight == validity_object.get("max_density_weight") and min_density_weight == validity_object.get("min_density_weight") or  rate_type in ["promotional", "consolidated"]:
                    if validity_object.get("validity_start") > validity_end:
                        new_validities.append(validity_object)
                        continue
                    if validity_object.get("validity_end") < validity_start:
                        new_validities.append(validity_object)
                        continue
                    if float(min_price) == 0.0:
                        min_price = validity_object.get("min_price")

                    if validity_object.get('validity_start') >= validity_start and validity_object.get('validity_end') <= validity_end and validity_id != validity_object.get('id'):
                        new_weight_slabs = self.merging_weight_slabs(validity_object.get('weight_slabs'), new_weight_slabs)
                        validity_object['status'] = False
                        new_validities.append(validity_object)
                        continue
                    if validity_object.get('validity_start') < validity_start and validity_object.get('validity_end') <= validity_end:
                        new_weight_slabs = self.merging_weight_slabs(validity_object.get('weight_slabs'), new_weight_slabs)
                        validity_object['validity_end'] = validity_start - datetime.timedelta(minutes=1)
                        new_validities.append(validity_object)
                        continue
                    if validity_object.get(validity_start) >= validity_start and validity_object.get('validity_end') > validity_end: 
                        new_weight_slabs = self.merging_weight_slabs(validity_object.get('weight_slabs'), new_weight_slabs)
                        validity_object['validity_start'] = validity_end + datetime.timedelta(minutes=1)
                        new_validities.append(validity_object)
                        continue
                    if validity_object.get('validity_start') < validity_start and validity_object.get('validity_end') > validity_end:
                        new_weight_slabs = self.merging_weight_slabs(validity_object.get('weight_slabs'), new_weight_slabs)
                        new_validities.append(AirFreightRateValidity(**{**validity_object, 'validity_end': validity_start - datetime.timedelta(days=1)}))
                        new_validities.append(AirFreightRateValidity(**{**validity_object, 'validity_start': validity_end + datetime.timedelta(days=1)}))
                        # params = self.audits.where(validity_id: old_validity1.id, action_name: ['create', 'update']).order('air_freight_rate_audits.created_at desc').first.as_json
                        # self.audits.create!(params.except('id', 'created_at', 'updated_at').merge!('validity_id' => old_validity2.id))
                        continue
                else:
                    new_validities.append(validity_object)
                
                if validity_id and validity_id == validity_object.get('id') and deleted:
                    validity_object['weight_slabs'] = new_weight_slabs
                    new_validities.append(validity_object)
                    self.min_price = validity_object.get("min_price")
                    continue

                if not deleted:
                    new_validity_object = {
                    "validity_start": validity_start,
                    "validity_end": validity_end,
                    "min_price": min_price,
                    "currency": currency,
                    "weight_slabs": new_weight_slabs,
                    "id": uuid.uuid1(),
                    "likes_count": 0,
                    "dislikes_count": 0,
                    "status": True,
                    "density_category": density_category,
                    "min_density_weight": min_density_weight,
                    "max_density_weight": max_density_weight,
                    "initial_volume": available_volume,
                    "available_volume": available_volume,
                    "initial_gross_weight": available_gross_weight,
                    "available_gross_weight": available_gross_weight
                    }
                
                new_validities.push(AirFreightRateValidity(**new_validity_object))
                self.min_price = new_validity_object["min_price"]
                new_validities = sorted(new_validities, key=lambda x: x['validity_end'])
                self.validities = new_validities
                if not deleted:
                    return new_validity_object['id']







    def merging_weight_slabs(self,old_weight_slabs,new_weight_slabs):
        final_old_weight_slabs = old_weight_slabs
        new_weight_slabs_currency = ""
        old_weight_slabs_currency = ""
        #     if new_weight_slabs.pluck('currency').uniq.first != final_old_weight_slabs.pluck('currency').uniq.first
        #   return new_weight_slabs

        for new_weight_slab in new_weight_slabs:
            final_old_weight_slabs = self.merge_slab(final_old_weight_slabs,new_weight_slab)

        return final_old_weight_slabs

    def merge_slab(old_weight_slabs,new_weight_slab):
        final_old_weight_slabs=[]
        for old_weight_slab in old_weight_slabs:
            if old_weight_slab['lower_limit'] >= int(new_weight_slab['upper_limit']):
                old_weight_slab['lower_limit'] = int(old_weight_slab['lower_limit']) + 0.1
                new_weight_slab['upper_limit'] = int(new_weight_slab['upper_limit'])
                final_old_weight_slabs.append(old_weight_slab)
                continue
            if int(old_weight_slab['upper_limit']) <= new_weight_slab['lower_limit']:
                old_weight_slab['upper_limit'] =int( old_weight_slab['upper_limit'])
                new_weight_slab['lower_limit'] = int(new_weight_slab['lower_limit']) + 0.1
                final_old_weight_slabs.append(old_weight_slab)
                continue
            if old_weight_slab['lower_limit'] >= int(new_weight_slab['lower_limit'] )and int(old_weight_slab['upper_limit']) <= new_weight_slab['upper_limit']:
                continue
            if int(old_weight_slab['lower_limit']) < new_weight_slab['lower_limit'] and int(old_weight_slab['upper_limit']) <= new_weight_slab['upper_limit']:
                old_weight_slab['upper_limit'] = int(new_weight_slab['lower_limit'])
                new_weight_slab['lower_limit'] = int(new_weight_slab['lower_limit']) + 0.1
                final_old_weight_slabs.append(old_weight_slab)
            if int(old_weight_slab['lower_limit']) >= int(new_weight_slab['lower_limit']) and old_weight_slab['upper_limit'] > int(new_weight_slab['upper_limit']):
                old_weight_slab['lower_limit'] = int(new_weight_slab['upper_limit']) + 0.1
                new_weight_slab['upper_limit'] = int(new_weight_slab['upper_limit'])
                final_old_weight_slabs.append(old_weight_slab)
            if int(old_weight_slab['lower_limit']) < new_weight_slab['lower_limit'] and int(old_weight_slab['upper_limit'])> new_weight_slab['upper_limit']:
                final_old_weight_slabs.append(WeightSlab(**{**old_weight_slab, 'upper_limit': int(new_weight_slab['lower_limit'])}))
                final_old_weight_slabs.append(WeightSlab(**{**old_weight_slab, 'lower_limit': int(new_weight_slab['upper_limit']) + 0.1}))

                new_weight_slab['lower_limit'] = new_weight_slab['lower_limit'] + 0.1
                new_weight_slab['upper_limit'] = new_weight_slab['upper_limit']
                continue
        final_old_weight_slabs.append(new_weight_slab)

        
        return final_old_weight_slabs


class AirFreightRateValidity(BaseModel):
    validity_start: datetime
    validity_end: datetime
    min_price: float
    id: str
    currency: str
    status: bool = True
    likes_count: int = None
    dislikes_count: int = None
    weight_slabs: list[WeightSlab] = []
    density_category: str = 'general'
    initial_volume: float = None
    available_volume: float = None
    initial_gross_weight: float = None
    available_gross_weight: float = None
    min_density_weight: float = None
    max_density_weight: float = None

    # class Config:
    #     orm_mode = True
    #     exclude = ('validity_start', 'validity_end')

    def validations(self):
        if self.initial_volume and self.initial_volume < 0:
            raise HTTPException(status_code=400,details = 'Initial Volume Should Be Positive')

        if self.available_volume and self.available_volume < 0:
            raise HTTPException(status_code=400,details = 'Available Volume Should Be Positive')
        
        if self.initial_gross_weight and self.initial_gross_weight < 0:
            raise HTTPException(status_code=400,details = 'Initial Gross Weight Be Positive')
        
        if self.available_gross_weight and self.available_gross_weight < 0:
            raise HTTPException(status_code=400,details = 'Available Gross Weight Be Positive')
        
        if self.min_density_weight and self.min_density_weight < 0:
            raise HTTPException(status_code=400,details = 'Minimum Density Weight Be Positive')
        
        if self.max_density_weight and self.max_density_weight < 0:
            raise HTTPException(status_code=400,details = 'Maximum Density Weight Be Positive')
        
        self.validate_weight_slabs()
        return True
    
    def validate_weight_slabs(self):
        now = datetime.now()
        beginning_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)

        if not self.status and self.validity_end < beginning_of_day:
            return
        lower_limits = []
        upper_limits = []
        check = False
        for slab in self.weight_slabs:
            if float(slab.get('upper_limit')) <= float(slab.get('lower_limit')):
                check = True
            lower_limits.append(slab.get('lower_limit'))
            upper_limits.append(slab.ge('upper_limit'))
        
        if check:
            raise HTTPException(status_code = 400,details = 'Invalid Weight Slabs')
        
        itr = 0

        while itr < len(upper_limits)-1:
            if float(upper_limits[itr]) >= float(lower_limits[itr+1]):
                raise HTTPException(status_code = 400,details = 'Weight Slabs OverLapping')
            itr = itr +1






    


    






