from fastapi.encoders import jsonable_encoder
from datetime import datetime
from micro_services.client import common
# import sentry_sdk
from services.chakravyuh.models.air_freight_rate_estimation import AirFreightRateEstimation
from services.chakravyuh.models.air_freight_rate_estimation_audit import AirFreightRateEstimationAudit
from database.rails_db import get_ff_mlo,get_past_invoices
from services.air_freight_rate.models.air_freight_clusters import AirFreightClusters
from services.air_freight_rate.models.air_freight_location_cluster_mapping import AirFreightLocationClusterMapping
from configs.global_constants import DEFAULT_WEIGHT_SLABS
from services.chakravyuh.producer_vyuhs.air_freight import AirFreightVyuh as AirProducerVyuh
class AirFreightVyuh():
    def __init__(self,
                new_rate: dict = {},  
                what_to_create: dict = {
                'country': True,
                }
                
            ):
        self.new_rate = jsonable_encoder(new_rate)
        self.weight = new_rate['weight']
        self.what_to_create = what_to_create
        self.weight_slabs = []
    
    def create_audits(self, data= {}):
        AirFreightRateEstimationAudit.create(**data)
    
    def get_transformations_to_be_affected(self):
        price_estimations_query = AirFreightRateEstimation.select(
            AirFreightRateEstimation.origin_location_id,
            AirFreightRateEstimation.origin_location_type,
            AirFreightRateEstimation.destination_location_id,
            AirFreightRateEstimation.destination_location_type,
            AirFreightRateEstimation.airline_id,
            AirFreightRateEstimation.commodity,
            AirFreightRateEstimation.operation_type,
            AirFreightRateEstimation.stacking_type,
            AirFreightRateEstimation.created_at,
            AirFreightRateEstimation.updated_at,
            AirFreightRateEstimation.shipment_type,
            AirFreightRateEstimation.weight_slabs,
            AirFreightRateEstimation.id,
            AirFreightRateEstimation.status
        ).where(
            AirFreightRateEstimation.origin_location_id << self.new_rate['origin_location_ids'],
            AirFreightRateEstimation.destination_location_id << self.new_rate['destination_location_ids'],
            ((AirFreightRateEstimation.operation_type == self.new_rate['operation_type']) | (AirFreightRateEstimation.operation_type.is_null(True))),
            ((AirFreightRateEstimation.airline_id.is_null(True)) | (AirFreightRateEstimation.airline_id == self.new_rate['airline_id'])),
            ((AirFreightRateEstimation.stacking_type.is_null(True)) | (AirFreightRateEstimation.stacking_type == self.new_rate['stacking_type'])),
            ((AirFreightRateEstimation.shipment_type.is_null(True)) | (AirFreightRateEstimation.shipment_type == self.new_rate['shipment_type'])),
            AirFreightRateEstimation.status == 'active'
        )

        price_estimations = jsonable_encoder(list(price_estimations_query.dicts()))
        return price_estimations
    
    def get_transformation(self, payload):
        created_tf = AirFreightRateEstimation.select(AirFreightRateEstimation.id).where(
                AirFreightRateEstimation.origin_location_id == payload['origin_location_id'],
                AirFreightRateEstimation.destination_location_id == payload['destination_location_id'],
                AirFreightRateEstimation.commodity == payload['commodity'],
                AirFreightRateEstimation.operation_type == payload['operation_type'],
                AirFreightRateEstimation.airline_id.is_null(True),
                AirFreightRateEstimation.stacking_type.is_null(True),
                AirFreightRateEstimation.shipment_type.is_null(True),
                AirFreightRateEstimation.status == 'active'
            ).limit(1)

        price_estimations = jsonable_encoder(list(created_tf.dicts()))
        if len(price_estimations):
            return price_estimations[0]
        return None
    
    def get_transformations_to_be_added(self, already_added_tranformations: list = []):
        must_have_transformations = [
            {
                "origin_location_id": self.new_rate['origin_country_id'],
                "origin_location_type": 'country',
                'destination_location_id': self.new_rate['destination_country_id'],
                'destination_location_type': 'country',
                'commodity': self.new_rate['commodity'],
                'operation_type': self.new_rate['operation_type'],
                'weight_slabs': [],
                'airline_id': None,
                'stacking_type': None,
                'shipment_type': None

            }

        ]
        not_available_transformations = []
        
        for mht in must_have_transformations:
            is_available = False
            for adt in already_added_tranformations:
                if (mht['origin_location_id'] == adt['origin_location_id'] and 
                    mht['origin_location_type'] == adt['origin_location_type'] and 
                    mht['destination_location_id'] == adt['destination_location_id'] and
                    mht['destination_location_type'] == adt['destination_location_type'] and
                    mht['commodity'] == adt['commodity'] and
                    mht['operation_type'] == adt['operation_type'] and
                    adt['airline_id'] == None and
                    adt['stacking_type'] == None and
                    adt['shipment_type'] == None

                ):
                    is_available = True
            if not is_available:
                not_available_transformations.append(mht)

        return not_available_transformations
    
    def get_price_from_invoices(self,slab):
        origin_airport_id = self.new_rate['origin_airport_id']
        destination_airport_id  = self.new_rate['destination_airport_id']
        old_rate = get_past_invoices(origin_airport_id,destination_airport_id,slab['lower_limit'],slab['upper_limit'])
        new_rate = self.new_rate['price']*0.8 + old_rate*0.2
        slab['lower_tariff_price'] = new_rate
        slab['upper_tariff_price'] = new_rate
        return slab
        
    def create_weight_slabs(self,weight_slabs):
        weight=self.weight
        x=2
        slab_index=0
        lower_tariff_price = 0
        upper_tariff_price =0
        for slab in weight_slabs:
            if int(slab['lower_limit'])<=weight<=int(slab['upper_limit']):
                slab = self.get_price_from_invoices(slab)
                lower_tariff_price = slab['lower_tariff_price']
                upper_tariff_price = slab['lower_tariff_price']
            slab_index+=1
        j=slab_index
        for i , slab in enumerate(weight_slabs):
            mf=pow(x,abs(i-j))
            rms_slab = {'lower_limit':0,'upper_limit':0,'tariff_price':0,'currency':'INR'}
            if i<slab_index:
                slab['lower_tariff_price']=mf*lower_tariff_price
                slab['upper_tariff_price'] = mf*upper_tariff_price
            if i > slab_index:
                slab['lower_tariff_price']=lower_tariff_price/mf
                slab['upper_tariff_price'] = mf*upper_tariff_price/mf
            rms_slab['lower_limit'] = slab['lower_limit']
            rms_slab['upper_limit'] = slab['upper_limit']
            rms_slab['tariff_price'] = slab['upper_tariff_price']
            rms_slab['currency'] = slab['currency']
            self.weight_slabs.append(rms_slab)
        return weight_slabs
    
    def get_adjusted_weight_slabs_to_add(self, affected_transformation: dict = {}, new:bool = False):

        weight_slabs = affected_transformation['weight_slabs'] or []
        if new:
            weight_slabs = DEFAULT_WEIGHT_SLABS 

        return self.create_weight_slabs(weight_slabs)

    
    def adjust_price_for_tranformation(self, affected_transformation, new: bool=False, is_relative: bool = False):
        from celery_worker import update_multiple_service_objects
        transformation_id = affected_transformation.get('id')
        # if is_relative:
        #     adjusted_weight_slabs = affected_transformation['weight_slabs']
        # else:
        #     adjusted_weight_slabs = self.get_adjusted_weight_slabs_to_add(affected_transformation, new)
        
        adjusted_weight_slabs = self.get_adjusted_weight_slabs_to_add(affected_transformation, new)

        if len(adjusted_weight_slabs) == 0:
            return
        
        # if not transformation_id and new:
        #     tf = self.get_transformation(affected_transformation)
        #     if tf:
        #         transformation_id = tf['id']
 
        if transformation_id:
            transformation = AirFreightRateEstimation.update(
                weight_slabs = adjusted_weight_slabs,
                updated_at = datetime.now()
            ).where(
                AirFreightRateEstimation.id == transformation_id
            ).execute()

            data = {
                'data': {
                    'weight_slabs': adjusted_weight_slabs,
                },
                'object_id': transformation_id,
                'action_name': 'update',
                'source': 'invoice'
            }
            # self.create_audits(data=data)
        else:
            payload = affected_transformation | {
                'weight_slabs': adjusted_weight_slabs,
            }
            transformation = AirFreightRateEstimation.create(
                origin_location_id = payload['origin_location_id'],
                origin_location_type = payload['origin_location_type'],
                destination_location_id = payload['destination_location_id'],
                destination_location_type=payload['destination_location_type'],
                operation_type =payload['operation_type'],
                shipment_type=payload['shipment_type'],
                weight_slabs=payload['weight_slabs'],
                airline_id=payload['airline_id'],
                commodity=payload['commodity'],
                stacking_type=payload['stacking_type'],
            )
            data = {
                'data': payload,
                'object_id': transformation.id,
                'action_name': 'create',
                'source': 'system'
            }
            affected_transformation['id'] = str(transformation.id)
            # self.create_audits(data=data)
            # transformation.set_attribute_objects()
        
        # if not is_relative:
        #     actual_transformation = affected_transformation
        #     actual_transformation['line_items'] = adjusted_line_items
        #     try:
        #         self.adjust_price_for_related_transformations(actual_transformation=actual_transformation)
        #     except Exception as e:
        #         sentry_sdk.capture_exception(e)
        
        return True




    def set_dynamic_pricing(self):
        '''
          Main Function to set dynamic pricing bounds  
        '''  
        from celery_worker import transform_dynamic_pricing
        
        affected_transformations = self.get_transformations_to_be_affected()
        new_transformations_to_add = self.get_transformations_to_be_added(affected_transformations)

        for affected_transformation in affected_transformations:
            if self.what_to_create[affected_transformation['origin_location_type']]:
                self.adjust_price_for_tranformation(affected_transformation=affected_transformation, new=False)
                # transform_dynamic_pricing.apply_async(kwargs={ 'new_rate': self.new_rate, 'current_validities': self.current_validities, 'affected_transformation': affected_transformation, 'new': False }, queue='low')
        
        for new_transformation in new_transformations_to_add:
            self.adjust_price_for_tranformation(affected_transformation=new_transformation, new=True)
            # transform_dynamic_pricing.apply_async(kwargs={ 'new_rate': self.new_rate, 'current_validities': self.current_validities, 'affected_transformation': new_transformation, 'new': True }, queue='low')

        insert_into_rms = self.rms_rates()
        return True
    

    def rms_rates(self):
        origin_airport_id = self.new_rate['origin_airport_id']
        destination_airport_id = self.new_rate['destination_airport_id']
        base_origin_airport  = AirFreightClusters.get_or_none(id=origin_airport_id)
        base_destination_airport = AirFreightClusters.get_or_none(id=origin_airport_id)
        all_rates=[]
        if base_origin_airport:
            origin_cluster_airports = self.get_all_cluster_airports(origin_airport_id)
            for clutser_airport in origin_cluster_airports:
                rate_params = self.get_rate_param(clutser_airport['location_id'],destination_airport_id,clutser_airport['factor'])
                all_rates.append(rate_params)


        if base_destination_airport:
            destination_cluster_airports = self.get_all_cluster_airports(origin_airport_id)
            for clutser_airport in destination_cluster_airports:
                rate_params = self.get_rate_param(origin_airport_id,clutser_airport['location_id'],clutser_airport['factor'])
                all_rates.append(rate_params)

        for rate in all_rates:
            producer = AirProducerVyuh(rate=rate)
            producer.extend_rate()
        
    def get_all_cluster_airports(self,base_airport_id):
        locations = AirFreightLocationClusterMapping.select(AirFreightLocationClusterMapping.location_id,
                            AirFreightLocationClusterMapping.rate_factor).where(
                                AirFreightLocationClusterMapping.base_airport_id==base_airport_id
                            )
        
        return  jsonable_encoder(list(locations.dicts()))
    
    def get_rate_param(self,origin_airport_id,destination_airport_id,factor):

        params = {
            'origin_aiport_id':origin_airport_id,
            'destination_airport_id':destination_airport_id,
            'commodity':self.new_rate.get('commodity'),
            'weight_slab':self.weight_slabs,
            'airline_id':self.new_rate.get('airline_id'),
            'operation_type':self.new_rate.get('operation_type'),
            'handling_type': 'stackable',
            'currency':self.new_rate['currency'],
            'price_type':'all_in',
            'min_price' : self.weight_slabs[0]['tariff_price'],
            'service_provider_id':'',
            'performed_by_id':'',
            'procured_by_id':'',
            'sourced_by_id':''

        }
        return params



# above adjust price

    # def get_related_transformations_to_add(self, actual_transformation: dict, commodities: list = [], operation_types:list = []):
    #     possible_transformations = []

    #     for cs in commodities:
    #         for ct in operation_types:
    #             possible_transformations.append({
    #                 'origin_location_id': actual_transformation['origin_location_id'],
    #                 'destination_location_id': actual_transformation['destination_location_id'],
    #                 'origin_location_type': actual_transformation['origin_location_type'],
    #                 'destination_location_type': actual_transformation['destination_location_type'],
    #                 'container_type': ct,
    #                 'container_size': cs,
    #                 'line_items': [],
    #                 'shipping_line_id': None,
    #                 'commodity': None,
    #                 'payment_term': None,
    #                 'schedule_type': None
    #             })

    #     tfs_query = AirFreightRateEstimation.select(
    #         AirFreightRateEstimation.origin_location_id,
    #         AirFreightRateEstimation.origin_location_type,
    #         AirFreightRateEstimation.destination_location_id,
    #         AirFreightRateEstimation.destination_location_type,
    #         AirFreightRateEstimation.airline_id,
    #         AirFreightRateEstimation.commodity,
    #         AirFreightRateEstimation.stacking_type,
    #         AirFreightRateEstimation.operation_type,
    #         AirFreightRateEstimation.created_at,
    #         AirFreightRateEstimation.updated_at,
    #         AirFreightRateEstimation.shipment_type,
    #         AirFreightRateEstimation.line_items,
    #         AirFreightRateEstimation.id,
    #         AirFreightRateEstimation.status
    #     ).where(
    #         AirFreightRateEstimation.origin_location_id == actual_transformation['origin_location_id'],
    #         AirFreightRateEstimation.destination_location_id == actual_transformation['destination_location_id'],
    #         AirFreightRateEstimation.commodity << commodities,
    #         AirFreightRateEstimation.operation_type << operation_types
    #     )

    #     already_created_tfs = jsonable_encoder(list(tfs_query.dicts())) or []

    #     already_created_tfs_hash = {}

    #     for act in already_created_tfs:
    #         key = '{}:{}:{}:{}:{}:{}'.format(
    #             act['origin_location_id'],
    #             act['origin_location_type'],
    #             act['destination_location_id'], 
    #             act['destination_location_type'],
    #             act['commodity'],
    #             act['operation_type']
    #             )
    #         line_items = act['line_items'] or []

    #         derived = None

    #         for line_item in line_items:
    #             if 'derived' in line_item:
    #                 derived = act['id']

    #         already_created_tfs_hash[key] = derived

    #     not_created_tfs = []

    #     for pst in possible_transformations:
    #         key = '{}:{}:{}:{}:{}:{}'.format(
    #             pst['origin_location_id'],
    #             pst['origin_location_type'],
    #             pst['destination_location_id'], 
    #             pst['destination_location_type'],
    #             pst['commodity'],
    #             pst['operation_type']
    #             )

    #         derived = already_created_tfs_hash.get(key)
    #         if key not in already_created_tfs_hash or derived:
    #             if derived:
    #                 pst['id'] = derived

    #             not_created_tfs.append(pst)
        
    #     return not_created_tfs
    
    # def get_relative_price(self, actual_transformation: dict, related_transformation: dict, line_item:dict):
    #     related_container_type = str(related_transformation['container_type'])
    #     related_container_size = str(related_transformation['container_size'])
    #     actual_container_size = str(actual_transformation['container_size'])
    #     actual_container_type = str(actual_transformation['container_type'])

    #     container_size_factor = CONTAINER_SIZE_FACTORS[actual_container_size]
    #     container_type_factor = CONTAINR_TYPE_FACTORS[actual_container_type]
    #     standard_rate_factor = 1 / container_size_factor
    #     standard_rate_factor = standard_rate_factor / container_type_factor
    #     realted_csf = CONTAINER_SIZE_FACTORS[related_container_size]
    #     realted_ctf = CONTAINR_TYPE_FACTORS[related_container_type]

    #     price = line_item['average']
    #     std_dev = line_item['stand_dev']
    #     related_rate_average = price * standard_rate_factor * realted_csf * realted_ctf
    #     lower_limit = related_rate_average - 1 * std_dev # -1 sigma
    #     upper_limit = related_rate_average + 1 * std_dev # 1 sigma
        
    #     return {
    #         'code': line_item['code'],
    #         'currency': self.target_currency,
    #         'upper_limit': round(upper_limit),
    #         'lower_limit': round(lower_limit),
    #         'average': related_rate_average,
    #         'stand_dev': std_dev,
    #         'size': line_item['size'],
    #         'unit': line_item['unit'],
    #         'derived': actual_transformation['id']
    #     }

    
    # def relative_price_to_add(self, actual_transformation: dict, related_transformation: dict):
    #     line_items = actual_transformation['line_items'] or []

    #     new_lineitems = []

    #     for line_item in line_items:
    #         related_lineitem = self.get_relative_price(actual_transformation, related_transformation, line_item)
    #         new_lineitems.append(related_lineitem)
        
    #     return new_lineitems

    # def adjust_price_for_related_transformations(self, actual_transformation):
    #     container_sizes = ['20', '40', '40HC', '45HC']
    #     container_sizes.remove(actual_transformation['container_size']) 
    #     container_types = ['standard', 'refer', 'open_top', 'open_side', 'flat_rack', 'iso_tank'] 
    #     container_types.remove(actual_transformation['container_type'])  

    #     related_transformations_to_add = self.get_related_transformations_to_add(actual_transformation, container_sizes, container_types)

    #     for rtf in related_transformations_to_add:
    #         # Insert price element to transformations
    #         rtf['line_items'] = self.relative_price_to_add(actual_transformation, rtf)
    #         self.adjust_price_for_tranformation(affected_transformation=rtf, new=False, is_relative=True)

