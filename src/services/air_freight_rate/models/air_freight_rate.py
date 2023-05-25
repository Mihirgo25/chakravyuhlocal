from peewee import *
from datetime import datetime,timedelta
from database.db_session import db
from fastapi import HTTPException
from configs.air_freight_rate_constants import MAX_CARGO_LIMIT

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class AirFreightRate(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    origin_airport_id=UUIDField(index=True,null=True)
    origin_country_id=UUIDField(null=True)
    origin_trade_id=UUIDField(null=True)
    origin_continent_id=UUIDField(null=True)
    destination_airport_id=UUIDField(index=True,null=True)
    destination_country_id=UUIDField(null=True)
    destination_trade_id=UUIDField(null=True)
    destination_continent_id=UUIDField(null=True)
    commodity=CharField(null=True,index=True)
    origin_airport=BinaryJSONField(null=True)
    destination_airport=BinaryJSONField(null=True)
    airline_id=UUIDField(null=True)
    service_provider_id=UUIDField(null=True)
    importer_exporter_id=UUIDField(null=True)
    min_price=FloatField(null=True)
    currency=CharField(null=True)
    discount_type=CharField(null=True)
    bookings_count=IntegerField(null=True)
    bookings_importer_exporters_count=IntegerField(null=True)
    spot_searches_count=IntegerField(null=True)
    spot_searches_importer_exporters_count=IntegerField(null=True)
    priority_score=IntegerField(null=True)
    priority_score_updated_at=DateTimeField(default=datetime.datetime.now,index=True)
    weight_slabs=BinaryJSONField(null=True)
    is_best_price=BooleanField(null=True)
    origin_local_id=UUIDField(null=True)
    destination_local_id=UUIDField(null=True)
    origin_local=BinaryJSONField(null=True)
    destination_local=BinaryJSONField(null=True)
    surcharge_id=UUIDField(null=True)
    airline=BinaryJSONField(null=True)
    service_provider=BinaryJSONField(null=True)
    warehouse_rate_id=UUIDField(null=True)
    rate_not_available_entry=BooleanField(null=True)
    origin_storage_id=UUIDField(null=True)
    destination_storage_id=UUIDField(null=True)
    origin_location_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, index=True, null=True)
    destination_location_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, index=True, null=True)
    operation_type=CharField(null=True)
    validities=BinaryJSONField(null=True)
    last_rate_available_date=DateTimeField(default=datetime.datetime.now,index=True)
    length=IntegerField(null=True)
    breadth=IntegerField(null=True)
    height=IntegerField(null=True)
    maximum_weight=IntegerField(null=True)
    shipment_type=CharField(null=True)
    stacking_type=CharField(null=True)
    commodity_sub_type=CharField(null=True)
    commodity_type=CharField(null=True)
    price_type=CharField(null=True)
    cogo_entity_id=UUIDField(null=True,index=True)
    rate_type=CharField(null=True)
    source=CharField(null=True)
    external_rate_id=UUIDField(null=True)
    flight_uuid=UUIDField(null=True)
    init_key = TextField(index=True, null=True)
    created_at=DateTimeField(default=datetime.datetime.now,index=True)
    updated_at=DateTimeField(default=datetime.datetime.now,index=True)
    sourced_by_id=UUIDField(null=True,index=True)
    procured_by_id=UUIDField(null=True,index=True)

    class Meta:
        table_name='air_freight_temp'

    def set_last_rate_available_date(self):
        new_validities = [validity for validity in self.validities if validity.get('status')]
        self.last_rate_available_date = new_validities[-1]['validity_end'] if new_validities else None


      
    
    def merging_weight_slabs(old_weight_slabs,new_weight_slab):
        final_old_weight_slabs=[]
        for old_weight_slab in old_weight_slabs:
            if old_weight_slab['lower_limit'] >= int(new_weight_slab['upper_limit']):
                old_weight_slab['lower_limit'] = int(old_weight_slab['lower_limit']) + 0.1
                new_weight_slab['upper_limit'] = int(new_weight_slab['upper_limit'])
                final_old_weight_slabs << old_weight_slab
                continue
            if int(old_weight_slab['upper_limit']) <= new_weight_slab['lower_limit']:
                old_weight_slab['upper_limit'] =int( old_weight_slab['upper_limit'])
                new_weight_slab['lower_limit'] = int(new_weight_slab['lower_limit']) + 0.1
                final_old_weight_slabs << old_weight_slab
                continue
            if int(old_weight_slab['lower_limit']) >= int(new_weight_slab['lower_limit'] )and int(old_weight_slab['upper_limit']) <= new_weight_slab['upper_limit']:
                continue
            if int(old_weight_slab['lower_limit']) < new_weight_slab['lower_limit'] and int(old_weight_slab['upper_limit']) <= new_weight_slab['upper_limit']:
                old_weight_slab['upper_limit'] = int(new_weight_slab['lower_limit'])
                new_weight_slab['lower_limit'] = int(new_weight_slab['lower_limit']) + 0.1
                final_old_weight_slabs << old_weight_slab
            if int(old_weight_slab['lower_limit']) >= int(new_weight_slab['lower_limit']) and old_weight_slab['upper_limit'] > int(new_weight_slab['upper_limit']):
                old_weight_slab['lower_limit'] = int(new_weight_slab['upper_limit']) + 0.1
                new_weight_slab['upper_limit'] = int(new_weight_slab['upper_limit'])
                final_old_weight_slabs << old_weight_slab
            if int(old_weight_slab['lower_limit']) < new_weight_slab['lower_limit'] and int(old_weight_slab['upper_limit'])> new_weight_slab['upper_limit']:
                old_weight_slab1 = AirFreightRateWeightSlab.new(old_weight_slab.as_json.deep_symbolize_keys.merge(upper_limit: new_weight_slab['lower_limit'].to_i))
                old_weight_slab2 = AirFreightRateWeightSlab.new(old_weight_slab.as_json.deep_symbolize_keys.merge(lower_limit: new_weight_slab['upper_limit'].to_i + 0.1))

                new_weight_slab['lower_limit'] = new_weight_slab['lower_limit'].to_i + 0.1
                new_weight_slab['upper_limit'] = new_weight_slab['upper_limit'].to_i

                final_old_weight_slabs << old_weight_slab1
                final_old_weight_slabs << old_weight_slab2
                continue
        final_old_weight_slabs << new_weight_slab
        
        return final_old_weight_slabs



            


    def validate_validity_object(validity_start,validity_end):

        if not validity_start:
            raise HTTPException(status_code=400,details='Validity Start is not Valid')
    
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
                
        for validity_object in self.validities:
            if  validity_object.density_category:
                validity_object.density_category = 'general'

            if validity_object.status ==False:
                new_validities.append(validity_object)
                continue
            if validity_object.density_category == 'high_density'  and  not deleted and  validity_object.density_category == density_category:
                if validity_object.min_density_weight < min_density_weight and validity_object.max_density_weight > min_density_weight:
                    validity_object.max_density_weight = min_density_weight
                if validity_object.min_density_weight > min_density_weight and max_density_weight > validity_object.min_density_weight:
                    max_density_weight = validity_object.min_density_weight
            if validity_object.density_category == density_category and max_density_weight == validity_object.max_density_weight and min_density_weight == validity_object.min_density_weight or  rate_type in ["promotional", "consolidated"]:
                if validity_object.validity_start > validity_end:
                    new_validities.append(validity_object)
                    continue
                if validity_object.validity_end < validity_start:
                    new_validities.append(validity_object)
                    continue
                if float(min_price) == 0.0:
                    min_price = validity_object.min_price
                if validity_object.validity_start >= validity_start and validity_object.validity_end <= validity_end and validity_id != validity_object.id:
                    new_weight_slabs = merging_weight_slabs(validity_object.weight_slabs, new_weight_slabs)
                    validity_object.status = False
                    continue
                if validity_object.validity_start < validity_start and validity_object.validity_end <= validity_end:
                    new_weight_slabs = merging_weight_slabs(validity_object.weight_slabs, new_weight_slabs)
                    validity_object.validity_end = validity_start - timedelta(minutes=1)
                    new_validities.append(validity_object)
                    continue
                if validity_object.validity_start >= validity_start and validity_object.validity_end > validity_end: 
                    new_weight_slabs = merging_weight_slabs(validity_object.weight_slabs, new_weight_slabs)
                    validity_object.validity_start = validity_end + 1.minute
                    new_validities.append(validity_object)
                    continue
                if validity_object.validity_start < validity_start and validity_object.validity_end > validity_end:
                    new_weight_slabs = merging_weight_slabs(validity_object.weight_slabs, new_weight_slabs)
                    old_validity1 = AirFreightRateValidity.new(validity_object.as_json.deep_symbolize_keys.merge(validity_end: validity_start - 1.minute))
                    old_validity2 = AirFreightRateValidity.new(validity_object.as_json.deep_symbolize_keys.merge(id: SecureRandom.uuid, validity_start: validity_end + 1.minute))
                    new_validities.append(old_validity1)
                    new_validities.append(old_validity2)
                    params = self.audits.where(validity_id: old_validity1.id, action_name: ['create', 'update']).order('air_freight_rate_audits.created_at desc').first.as_json
                    self.audits.create!(params.except('id', 'created_at', 'updated_at').merge!('validity_id' => old_validity2.id))
                    continue




                    

