from fastapi.encoders import jsonable_encoder
from datetime import datetime,timedelta
from micro_services.client import common
# import sentry_sdk
from services.chakravyuh.models.air_freight_rate_estimation import AirFreightRateEstimation
from services.chakravyuh.models.air_freight_rate_estimation_audit import AirFreightRateEstimationAudit
from database.rails_db import get_past_air_invoices
from services.air_freight_rate.models.air_freight_location_cluster import AirFreightLocationCluster
from services.air_freight_rate.models.air_freight_location_cluster_mapping import AirFreightLocationClusterMapping
from services.air_freight_rate.constants.air_freight_rate_constants import DEFAULT_FACTORS_WEIGHT_SLABS
from services.chakravyuh.producer_vyuhs.air_freight import AirFreightVyuh as AirProducerVyuh
from statistics import mean
from services.air_freight_rate.constants.air_freight_rate_constants import DEFAULT_SERVICE_PROVIDER_ID,DEFAULT_FACTOR
from configs.env import DEFAULT_USER_ID
from services.air_freight_rate.models.air_freight_location_cluster_factor import AirFreightLocationClusterFactor
from services.air_freight_rate.models.air_freight_rate_airline_factors import AirFreightAirlineFactors
from services.air_freight_rate.helpers.get_matching_weight_slab import get_matching_slab
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
class AirFreightVyuh():
    def __init__(self,
                new_rate: dict = {},  
                what_to_create: dict = {
                'country': True,
                },
                csr:bool = False
                
            ):
        self.new_rate = jsonable_encoder(new_rate)
        self.weight = new_rate.get('weight')
        self.what_to_create = what_to_create
        self.weight_slabs = []
        self.months = 3
        self.csr = csr
    
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
            AirFreightRateEstimation.origin_location_id == self.new_rate['origin_country_id'],
            AirFreightRateEstimation.destination_location_id == self.new_rate['destination_country_id'],
            AirFreightRateEstimation.operation_type == self.new_rate['operation_type'],
            AirFreightRateEstimation.commodity == self.new_rate['commodity'],
            ((AirFreightRateEstimation.airline_id.is_null(True)) | (AirFreightRateEstimation.airline_id == self.new_rate.get('airline_id'))),
            ((AirFreightRateEstimation.stacking_type.is_null(True)) | (AirFreightRateEstimation.stacking_type == self.new_rate.get('stacking_type'))),
            ((AirFreightRateEstimation.shipment_type.is_null(True)) | (AirFreightRateEstimation.shipment_type == self.new_rate.get('shipment_type'))),
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
    
    def split_invoice_data(self,previous_invoice_rates):
        last_2_months=[]
        last_3rdmonth=[]
        for invoice in previous_invoice_rates:
            if datetime.now().month - invoice['invoice_date'].month> 2:
                last_3rdmonth.append(invoice)
            else:
                last_2_months.append(invoice)
        return last_2_months,last_3rdmonth
    

    def get_weight_slabs(self,invoice_rates):
        weight_slabs = DEFAULT_FACTORS_WEIGHT_SLABS
        weight_slabs_dict= {1:[],2:[],3:[],4:[],5:[],6:[]}
        for invoice_rate in invoice_rates:
            for index,weight_slab in enumerate(weight_slabs):
                weight=invoice_rate['weight']
                if weight>=weight_slab['lower_limit'] and weight<=weight_slab['upper_limit']:
                    price = float(invoice_rate['price'])
                    if invoice_rate['currency']!='INR':
                        price = common.get_money_exchange_for_fcl({"price": price, "from_currency": invoice_rate['currency'], "to_currency": 'INR' })['price']
                    weight_slabs_dict[index+1].append(price)
        
        new_weight_slabs = []

        for index,weight_slab in enumerate(weight_slabs):
            new_weight_slab = jsonable_encoder(weight_slab)
            if weight_slabs_dict[index+1]:
                new_weight_slab['tariff_price'] = mean(weight_slabs_dict[index+1])
            new_weight_slabs.append(new_weight_slab)

        return new_weight_slabs
    
    def get_final_invoice_prices(self, origin_location_id, destination_location_id, location_type):
        
        past_air_invoices = get_past_air_invoices(origin_location_id, destination_location_id, location_type, self.months,'month','months')

        actual_invoice_data = []

        for past_air_invoice in past_air_invoices:
            new_past_air_invoice = {
                "origin_airport_id": past_air_invoice['origin_airport_id'],   
                "volume": past_air_invoice['volume'],   
                "is_stackable": past_air_invoice['is_stackable'],      
                "origin_country_id": past_air_invoice['origin_country_id'],
                "destination_airport_id": past_air_invoice['destination_airport_id'],
                "destination_country_id": past_air_invoice['destination_country_id'],
                "operation_type": past_air_invoice['operation_type'],
                "weight": past_air_invoice['weight'],
                "commodity": past_air_invoice['commodity'],
                "invoice_date": past_air_invoice['invoice_date'],
                "airline_id": past_air_invoice['airline_id'],
                'chargeable_weight': past_air_invoice['chargeable_weight']
            }
            line_items = past_air_invoice['line_items']
            actual_lineitem = None
            bas_count = 0
            for line_item in line_items:
                if line_item['code'] == 'BAS' and line_item['unit'] == 'per_kg':
                    actual_lineitem = line_item
                    bas_count = bas_count + 1
                if line_item['code'] == 'BAS' and line_item['unit'] == 'per_shipment' and not actual_lineitem:
                    actual_lineitem = line_item
                    bas_count = bas_count + 1
                    actual_lineitem['price'] = (line_item['price'] / (new_past_air_invoice['chargeable_weight'] or new_past_air_invoice['weight']))

            if actual_lineitem and bas_count == 1:
                new_past_air_invoice['price'] = actual_lineitem['price']
                new_past_air_invoice['unit'] = actual_lineitem['unit']
                new_past_air_invoice['currency'] = actual_lineitem['currency']
                actual_invoice_data.append(new_past_air_invoice)

        return actual_invoice_data

        
    def create_weight_slabs(self,origin_location_id,destination_location_id,location_type):

        previous_invoice_rates = self.get_final_invoice_prices(origin_location_id,destination_location_id,location_type)

        prevoius_2month_invoice_rates,previous_3rd_month_rates=self.split_invoice_data(previous_invoice_rates)

        latest_weight_slabs=self.get_weight_slabs(prevoius_2month_invoice_rates)
        old_weight_slabs=self.get_weight_slabs(previous_3rd_month_rates)
        missing_weight_slabs = self.find_missing_weight_slabs(latest_weight_slabs)
        missing_weight_slabs_ratios = self.raito_finder(old_weight_slabs, missing_weight_slabs)
        final_weight_slabs = self.calculate_missing_rate(missing_weight_slabs_ratios,latest_weight_slabs)
        return final_weight_slabs
    

    def find_missing_weight_slabs(self,weight_slabs):
        missing_slabs =[]
        for index , weight_slab in enumerate(weight_slabs):
            if weight_slab['tariff_price']==0:
                missing_slabs.append(index +1)
        return missing_slabs
    
    def raito_finder(self,old_weight_slabs,missing_weight_slabs):
        ratios={}
        for old_slab_index,weight_slab in enumerate(old_weight_slabs):
            for index in missing_weight_slabs:
                if weight_slab['tariff_price']!= 0 and old_weight_slabs[index-1]['tariff_price']!=0 and old_slab_index+1!=index:
                    ratio=weight_slab['tariff_price'] / old_weight_slabs[index-1]['tariff_price']
                    ratios[f'{old_slab_index+1}:{index}'] =ratio
        return ratios
    
    def calculate_missing_rate(self,ratios,latest_weight_slabs):
        final_weight_slabs = []
        rate_index = -1
        price = self.new_rate['price']
        for index,weight_slab in enumerate(latest_weight_slabs):
            if self.new_rate['weight'] >= weight_slab['lower_limit'] and self.new_rate['weight'] <= weight_slab['upper_limit']:
                if weight_slab['currency']!=self.new_rate['currency']:
                    price = common.get_money_exchange_for_fcl({"price": price, "from_currency": self.new_rate['currency'], "to_currency": 'INR' })['price']
                weight_slab['tariff_price'] = 0.2*weight_slab['tariff_price'] + 0.8*price
                rate_index = index

        for index1, weight_slab1 in enumerate( latest_weight_slabs):
            if weight_slab1['tariff_price']==0.0:
                for index2,weight_slab2 in enumerate(latest_weight_slabs):
                    if weight_slab2['tariff_price']!=0.0:
                        key = "{}:{}".format(index2+1,index1+1)
                        if key in ratios.keys():
                            weight_slab1['tariff_price'] = weight_slab2['tariff_price'] / ratios[key]
                            break
                if index1<rate_index:
                    factor=(pow(DEFAULT_FACTOR,rate_index-index1))
                    weight_slab1['tariff_price']=price/factor
                if index1 > rate_index:
                    factor=(pow(DEFAULT_FACTOR,index1-rate_index))
                    weight_slab1['tariff_price']=price*factor
            final_weight_slabs.append(weight_slab1)
        
 
        return jsonable_encoder(final_weight_slabs)


    def get_adjusted_weight_slabs_to_add(self, affected_transformation, new):

        weight_slabs = self.create_weight_slabs(affected_transformation['origin_location_id'], affected_transformation['destination_location_id'], affected_transformation['origin_location_type'])
        new_weight_slabs = []
        for weight_slab in weight_slabs:
            weight_slab['avg_price'] = weight_slab['tariff_price']
            weight_slab['lower_tariff_price'] = weight_slab['tariff_price']
            weight_slab['upper_tariff_price'] = weight_slab['tariff_price']
            del weight_slab['tariff_price']
            new_weight_slabs.append(weight_slab)

        return new_weight_slabs

    
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
        
        if not transformation_id and new:
            tf = self.get_transformation(affected_transformation)
            if tf:
                transformation_id = tf['id']

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
            self.create_audits(data=data)
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
            self.create_audits(data=data)
            transformation.set_attribute_objects()
        
        # if not is_relative:
        #     actual_transformation = affected_transformation
        #     actual_transformation['line_items'] = adjusted_line_items
        #     try:
        #         self.adjust_price_for_related_transformations(actual_transformation=actual_transformation)
        #     except Exception as e:
        #         sentry_sdk.capture_exception(e)
        
        return True




    def set_estimations(self):
        from celery_worker import transform_air_dynamic_pricing
        
        affected_transformations = self.get_transformations_to_be_affected()
        new_transformations_to_add = self.get_transformations_to_be_added(affected_transformations)

        for affected_transformation in affected_transformations:
            if self.what_to_create[affected_transformation['origin_location_type']]:
                # self.adjust_price_for_tranformation(affected_transformation=affected_transformation, new=False)
                transform_air_dynamic_pricing.apply_async(kwargs={ 'new_rate': self.new_rate, 'affected_transformation': affected_transformation, 'new': False }, queue='low')
        
        for new_transformation in new_transformations_to_add:
            # self.adjust_price_for_tranformation(affected_transformation=new_transformation, new=True)
            transform_air_dynamic_pricing.apply_async(kwargs={ 'new_rate': self.new_rate, 'affected_transformation': new_transformation, 'new': True }, queue='low')

        return True
    
    def get_factors(self,origin_cluster_id,destination_cluster_id,cluster_ids):
        query = AirFreightLocationClusterFactor.select(
            AirFreightLocationClusterFactor.rate_factor,
            AirFreightLocationClusterFactor.cluster_id,
            AirFreightLocationClusterFactor.location_id).where(
            AirFreightLocationClusterFactor.cluster_id << cluster_ids,
            AirFreightLocationClusterFactor.status == 'active',
            AirFreightLocationClusterFactor.origin_cluster_id == origin_cluster_id,
            AirFreightLocationClusterFactor.destination_cluster_id == destination_cluster_id
            )
        
        return jsonable_encoder(list(query.dicts()))
    
    def get_cluster_rate_combinations(self,weight_slabs):
        origin_airport_id = self.new_rate['origin_airport_id']
        destination_airport_id = self.new_rate['destination_airport_id']

        clusters_query  = AirFreightLocationCluster.select(
                AirFreightLocationCluster.id,
                AirFreightLocationCluster.base_airport_id
            ).where(
                AirFreightLocationCluster.base_airport_id in [origin_airport_id, destination_airport_id],
                AirFreightLocationCluster.status == 'active'
            )
        clusters = jsonable_encoder(list(clusters_query.dicts()))
        
        origin_cluster_id = None
        destination_cluster_id = None

        for cluster in clusters:
            if cluster['base_airport_id'] == origin_airport_id:
                origin_cluster_id = cluster['id']
            if cluster['base_airport_id'] == destination_airport_id:
                destination_cluster_id = cluster['id']

        cluster_ids = []
        if origin_cluster_id:
            cluster_ids.append(origin_cluster_id)
        
        if destination_cluster_id:
            cluster_ids.append(destination_cluster_id)

        all_rates = []
        if cluster_ids:
            location_cluster_ids = []
            if not origin_cluster_id:
                cluster = AirFreightLocationClusterMapping.select(AirFreightLocationClusterMapping.cluster_id).where(
                    AirFreightLocationClusterMapping.location_id == origin_airport_id
                ).first()
                origin_cluster_id = cluster.cluster_id
            else:
                location_cluster_ids.append(origin_cluster_id)
            
            if not destination_cluster_id:
                cluster = AirFreightLocationClusterMapping.select(AirFreightLocationClusterMapping.cluster_id).where(
                    AirFreightLocationClusterMapping.location_id == destination_airport_id
                ).first()
                destination_cluster_id = cluster.cluster_id
            else:
                location_cluster_ids.append(destination_cluster_id)


            factors_mappings = self.get_factors(origin_cluster_id,destination_cluster_id,location_cluster_ids)
            for factor_mapping in factors_mappings:
                if factor_mapping['cluster_id'] == origin_cluster_id:
                    rate_params = self.get_rate_param(factor_mapping['location_id'],destination_airport_id,weight_slabs,factor_mapping['rate_factor'])
                
                if factor_mapping['cluster_id'] == destination_cluster_id:
                    rate_params = self.get_rate_param(origin_airport_id,factor_mapping['location_id'],weight_slabs,factor_mapping['rate_factor'])
                all_rates.append(rate_params)
        rate_params = self.get_rate_param(origin_airport_id,destination_airport_id,weight_slabs)
        all_rates.append(rate_params)
        return all_rates

    def insert_rates_to_rms(self):
        from celery_worker import extend_air_freight_rates
        origin_airport_id = self.new_rate['origin_airport_id']
        destination_airport_id = self.new_rate['destination_airport_id']
        if self.csr:
            weight_slabs = self.new_rate.get('weight_slabs')
        else:
            weight_slabs = self.create_weight_slabs(origin_airport_id,destination_airport_id,'airport')
        rates_to_extend = self.get_cluster_rate_combinations(weight_slabs)
        for rate in rates_to_extend:
            from services.chakravyuh.producer_vyuhs.air_freight import AirFreightVyuh as Producer
            t = Producer(rate=rate)
            t.extend_rate(source='rate_extension')
            # extend_air_freight_rates.apply_async(kwargs={ 'rate': rate, 'source': 'invoice' }, queue='low')
    
    def get_rate_param(self,origin_airport_id,destination_airport_id,weight_slabs,factor=1 ):
        params = {
            'origin_airport_id':origin_airport_id,
            'destination_airport_id':destination_airport_id,
            'commodity':self.new_rate.get('commodity'),
            'commodity_type': 'all' if self.new_rate.get('commodity') == 'general' else 'other_special',
            'commodity_sub_type': 'all' if self.new_rate.get('commodity') == 'general' else 'others',
            'weight_slabs':self.get_rms_weight_slabs(weight_slabs=weight_slabs,factor=factor,origin_airport_id=origin_airport_id,destination_airport_id=destination_airport_id,airline=self.new_rate.get('airline_id')),
            'airline_id':self.new_rate.get('airline_id'),
            'operation_type':self.new_rate.get('operation_type'),
            'stacking_type': 'stackable' if (self.new_rate.get('is_stackable') or self.new_rate.get('is_stackable') == None) else 'non_stackable',
            'shipment_type':self.new_rate['shipment_type'],
            'currency':weight_slabs[0]['currency'],
            'price_type':'net_net',
            'min_price' : weight_slabs[0]['tariff_price'],
            'service_provider_id':DEFAULT_SERVICE_PROVIDER_ID,
            'performed_by_id':DEFAULT_USER_ID,
            'procured_by_id':DEFAULT_USER_ID,
            'sourced_by_id':DEFAULT_USER_ID,
            'validity_start': datetime.now().date(),
            'validity_end': datetime.now().date() + timedelta(days=7),
            'rate_type': 'market_place',
            'density_category': 'general',
            'density_ratio':'1:1',
            'length':300,
            'breadth':300,
            'height':300
        }
        if self.csr:
            params['commodity_sub_type'] = self.new_rate.get('commodity_sub_type')
            params['commodity_type'] = self.new_rate.get('commodity_type')
            params['stacking_type'] = self.new_rate.get('stacking_type')



        return params
    
    def get_rms_weight_slabs(self,weight_slabs,factor,origin_airport_id,destination_airport_id,airline):
        new_weight_slabs = jsonable_encoder(weight_slabs)
        airline_factors = AirFreightAirlineFactors.select(AirFreightAirlineFactors.slab_wise_factor).where(
            AirFreightAirlineFactors.origin_airport_id == origin_airport_id,
            AirFreightAirlineFactors.destination_airport_id == destination_airport_id,
            AirFreightAirlineFactors.derive_airline_id == airline,
            AirFreightAirlineFactors.base_airline_id == self.new_rate.get('airline_id')
        ).first()
        if not airline_factors:
            airline_factors = {
            "0.0-45":1,
            "45-100":1,
            "100-300":1,
            "300-500":1,
            "500-5000":1,
        }

        for weight_slab in new_weight_slabs:
            matching_slab = get_matching_slab(weight_slab['lower_limit'])
            weight_slab['tariff_price'] = factor*weight_slab['tariff_price']*airline_factors[matching_slab]
        return new_weight_slabs
    
    def set_dynamic_pricing(self):
        self.set_estimations()
        # self.insert_rates_to_rms()
        return True
