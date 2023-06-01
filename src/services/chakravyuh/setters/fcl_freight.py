from fastapi.encoders import jsonable_encoder
from datetime import datetime
from micro_services.client import common
import sentry_sdk
from configs.fcl_freight_rate_constants import DEFAULT_RATE_TYPE
from services.chakravyuh.models.fcl_freight_rate_estimation import FclFreightRateEstimation
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.chakravyuh.models.fcl_freight_rate_estimation_audit import FclFreightRateEstimationAudit
from database.rails_db import get_ff_mlo
from configs.transformation_constants import CONTAINR_TYPE_FACTORS, CONTAINER_SIZE_FACTORS

class FclFreightVyuh():
    def __init__(self,
                new_rate: dict = {}, 
                current_validities: dict = [], 
                what_to_create: dict = {
                'seaport': True,
                'country': False,
                'trade': False
                }
            ):
        self.new_rate = jsonable_encoder(new_rate)
        self.current_validities = current_validities
        self.target_currency = 'USD'
        self.ff_mlo = get_ff_mlo()
        self.what_to_create = what_to_create
    
    def create_audits(self, data= {}):
        FclFreightRateEstimationAudit.create(**data)
    
    def get_transformations_to_be_affected(self):
        price_estimations_query = FclFreightRateEstimation.select(
            FclFreightRateEstimation.origin_location_id,
            FclFreightRateEstimation.origin_location_type,
            FclFreightRateEstimation.destination_location_id,
            FclFreightRateEstimation.destination_location_type,
            FclFreightRateEstimation.shipping_line_id,
            FclFreightRateEstimation.commodity,
            FclFreightRateEstimation.container_size,
            FclFreightRateEstimation.container_type,
            FclFreightRateEstimation.created_at,
            FclFreightRateEstimation.updated_at,
            FclFreightRateEstimation.schedule_type,
            FclFreightRateEstimation.payment_term,
            FclFreightRateEstimation.line_items,
            FclFreightRateEstimation.id,
            FclFreightRateEstimation.status
        ).where(
            FclFreightRateEstimation.origin_location_id << self.new_rate['origin_location_ids'],
            FclFreightRateEstimation.destination_location_id << self.new_rate['destination_location_ids'],
            FclFreightRateEstimation.container_size == self.new_rate['container_size'],
            FclFreightRateEstimation.container_type == self.new_rate['container_type'],
            ((FclFreightRateEstimation.schedule_type.is_null(True)) | (FclFreightRateEstimation.schedule_type == self.new_rate['schedule_type'])),
            ((FclFreightRateEstimation.payment_term.is_null(True)) | (FclFreightRateEstimation.payment_term == self.new_rate['payment_term'])),
            ((FclFreightRateEstimation.commodity.is_null(True)) | (FclFreightRateEstimation.commodity == self.new_rate['commodity'])),
            ((FclFreightRateEstimation.shipping_line_id.is_null(True)) | (FclFreightRateEstimation.shipping_line_id == self.new_rate['shipping_line_id'])),
            FclFreightRateEstimation.status == 'active'
        )

        price_estimations = jsonable_encoder(list(price_estimations_query.dicts()))
        return price_estimations
    
    def get_transformation(self, payload):
        created_tf = FclFreightRateEstimation.select(FclFreightRateEstimation.id).where(
                FclFreightRateEstimation.origin_location_id == payload['origin_location_id'],
                FclFreightRateEstimation.destination_location_id == payload['destination_location_id'],
                FclFreightRateEstimation.container_size == payload['container_size'],
                FclFreightRateEstimation.container_type == payload['container_type'],
                FclFreightRateEstimation.schedule_type.is_null(True),
                FclFreightRateEstimation.payment_term.is_null(True),
                FclFreightRateEstimation.commodity.is_null(True),
                FclFreightRateEstimation.shipping_line_id.is_null(True),
                FclFreightRateEstimation.status == 'active'
            ).limit(1)

        price_estimations = jsonable_encoder(list(created_tf.dicts()))
        if len(price_estimations):
            return price_estimations[0]
        return None
    
    def get_transformations_to_be_added(self, already_added_tranformations: list = []):
        must_have_transformations = [
            {
                "origin_location_id": self.new_rate['origin_port_id'],
                "origin_location_type": 'seaport',
                'destination_location_id': self.new_rate['destination_port_id'],
                'destination_location_type': 'seaport',
                'container_size': self.new_rate['container_size'],
                'container_type': self.new_rate['container_type'],
                'line_items': [],
                'shipping_line_id': None,
                'commodity': None,
                'payment_term': None,
                'schedule_type': None

            },
            {
                "origin_location_id": self.new_rate['origin_country_id'],
                "origin_location_type": 'country',
                'destination_location_id': self.new_rate['destination_country_id'],
                'destination_location_type': 'country',
                'container_size': self.new_rate['container_size'],
                'container_type': self.new_rate['container_type'],
                'line_items': [],
                'shipping_line_id': None,
                'commodity': None,
                'payment_term': None,
                'schedule_type': None
            },
            {
                "origin_location_id": self.new_rate['origin_trade_id'],
                "origin_location_type": 'trade',
                'destination_location_id': self.new_rate['destination_trade_id'],
                'destination_location_type': 'trade',
                'container_size': self.new_rate['container_size'],
                'container_type': self.new_rate['container_type'],
                'line_items': [],
                'shipping_line_id': None,
                'commodity': None,
                'payment_term': None,
                'schedule_type': None
            },

        ]

        not_available_transformations = []
        
        for mht in must_have_transformations:
            is_available = False
            for adt in already_added_tranformations:
                if (mht['origin_location_id'] == adt['origin_location_id'] and 
                    mht['origin_location_type'] == adt['origin_location_type'] and 
                    mht['destination_location_id'] == adt['destination_location_id'] and
                    mht['destination_location_type'] == adt['destination_location_type'] and
                    mht['container_size'] == adt['container_size'] and
                    mht['container_type'] == adt['container_type'] and
                    adt['schedule_type'] == None and
                    adt['payment_term'] == None and
                    adt['commodity'] == None and
                    adt['shipping_line_id'] == None

                ):
                    is_available = True
            if not is_available:
                not_available_transformations.append(mht)

        return not_available_transformations
    
    def get_validity_matching_current_date(self, rate: dict = {}):
        matching_validity = None
        current_date =  datetime.now().date()
        rate_validities = rate['validities'] or []
        for validity in rate_validities:
            if current_date <= datetime.fromisoformat(validity['validity_end']).date():
                matching_validity = validity
                break
        return matching_validity    
    
    def get_available_rates_of_transormation(self, affected_transformation):
        current_date =  datetime.now().date()
        rates_query = FclFreightRate.select(
            FclFreightRate.id, 
            FclFreightRate.validities,
            FclFreightRate.service_provider_id,
            FclFreightRate.shipping_line_id,
            FclFreightRate.commodity,
            FclFreightRate.origin_port_id,
            FclFreightRate.destination_port_id,
            FclFreightRate.origin_country_id,
            FclFreightRate.destination_country_id,
            FclFreightRate.origin_trade_id,
            FclFreightRate.destination_trade_id
        ).where(
            FclFreightRate.id != self.new_rate['id'],
            FclFreightRate.service_provider_id.in_(self.ff_mlo),
            FclFreightRate.container_size == affected_transformation['container_size'],
            FclFreightRate.container_type == affected_transformation['container_type'],
            ~FclFreightRate.rate_not_available_entry,
            FclFreightRate.last_rate_available_date >= current_date,
            FclFreightRate.mode != 'predicted',
            FclFreightRate.rate_type == DEFAULT_RATE_TYPE
        )

        if affected_transformation['origin_location_type'] == 'seaport':
            rates_query = rates_query.where(
                FclFreightRate.origin_port_id == affected_transformation['origin_location_id'],
                FclFreightRate.destination_port_id == affected_transformation['destination_location_id']
            )
        elif affected_transformation['origin_location_type'] == 'country':
            rates_query = rates_query.where(
                FclFreightRate.origin_country_id == affected_transformation['origin_location_id'],
                FclFreightRate.destination_country_id == affected_transformation['destination_location_id']
            )
        elif affected_transformation['origin_location_type'] == 'trade':
            rates_query = rates_query.where(
                FclFreightRate.origin_trade_id == affected_transformation['origin_location_id'],
                FclFreightRate.destination_trade_id == affected_transformation['destination_location_id']
            )
        else:
            return None
        
        if 'shipping_line_id' in affected_transformation and affected_transformation['shipping_line_id']:
            rates_query = rates_query.where(FclFreightRate.shipping_line_id == affected_transformation['shipping_line_id'])
        
        if affected_transformation['commodity']:
            rates_query = rates_query.where(FclFreightRate.commodity == affected_transformation['commodity'])

        current_available_rates = jsonable_encoder(list(rates_query.dicts())) or []

        # Add newly added rate for calculation

        current_available_rates.append({
            'validities': self.current_validities,
            'id': self.new_rate['id']
        })

        return current_available_rates
    
    def get_eligible_rate_lineitems(self, current_available_rates, line_item_code):
        matching_validities = []
        for rate in current_available_rates:
            matching_validity = self.get_validity_matching_current_date(rate=rate)
            if matching_validity:
                matching_validities.append(matching_validity)
        
        matching_line_items = []

        for validity in matching_validities:
            line_items = validity['line_items']

            for line_item in line_items:
                if line_item['code'] == line_item_code:
                    matching_line_items.append(line_item)
        return matching_line_items

    
    def get_lower_and_upper_limit_for_transformation_line_item(self, line_item: dict, affected_transformation):
        current_available_rates = self.get_available_rates_of_transormation(affected_transformation)
        
        line_item_code = line_item['code']

        matching_line_items = self.get_eligible_rate_lineitems(current_available_rates, line_item_code)

        all_prices = []

        for matching_lineitem in matching_line_items:
            price = matching_lineitem['price']
            converted_price = price
            if matching_lineitem['currency'] != self.target_currency:
                converted_price = common.get_money_exchange_for_fcl({"price": price, "from_currency": matching_lineitem['currency'], "to_currency": self.target_currency })['price']
            
            all_prices.append(converted_price)
        
        size = len(all_prices)
        mean = sum(all_prices) / size
        variance = sum([((x - mean) ** 2) for x in all_prices]) / size
        std_dev = variance ** 0.5
        lower_limit = mean - 1 * std_dev # -1 sigma
        upper_limit = mean + 1 * std_dev # 1 sigma
        
        return {
            'code': line_item_code,
            'currency': self.target_currency,
            'upper_limit': round(upper_limit),
            'lower_limit': round(lower_limit),
            'average': mean,
            'stand_dev': std_dev,
            'size': size,
            'unit': line_item['unit']
        }
        
    def new_sigma_values(self, old_item, new_item):
        if 'average' not in old_item:
            return new_item
        
        size = new_item['size']
        old_mean = old_item['average']
        new_mean = new_item['average']
        exp_average = old_mean * 0.8 + new_mean * 0.2
        old_variance = new_item['stand_dev'] ** 2
        new_variance = ((size - 1) * old_variance + size * (new_mean - old_mean) ** 2) / size
        std_dev = new_variance ** 0.5
        lower_limit = exp_average - 1 * std_dev # -1 sigma
        upper_limit = exp_average + 1 * std_dev # 1 sigma
        
        return {
            'code': new_item['code'],
            'currency': new_item['currency'],
            'upper_limit': round(upper_limit),
            'lower_limit': round(lower_limit),
            'average': exp_average,
            'stand_dev': std_dev,
            'size': size,
            'unit': new_item['unit']
        }
    
    def get_adjusted_line_items_to_add(self, affected_transformation: dict = {}, new:bool = False):
        line_items = affected_transformation['line_items'] or []
        new_line_items = []

        derived = False

        for line_item in line_items:
            if 'derived' in line_item:
                derived = True

        if new or derived:
            line_items = self.new_rate['line_items'] or []

        for line_item in line_items:
            if line_item['code'] == 'BAS':
                new_line_item = self.get_lower_and_upper_limit_for_transformation_line_item(line_item, affected_transformation)
                new_line_item = self.new_sigma_values(line_item, new_line_item)
                new_line_items.append(new_line_item)

        return new_line_items
    
    def get_related_transformations_to_add(self, actual_transformation: dict, container_sizes: list = [], container_types:list = []):
        possible_transformations = []

        for cs in container_sizes:
            for ct in container_types:
                possible_transformations.append({
                    'origin_location_id': actual_transformation['origin_location_id'],
                    'destination_location_id': actual_transformation['destination_location_id'],
                    'origin_location_type': actual_transformation['origin_location_type'],
                    'destination_location_type': actual_transformation['destination_location_type'],
                    'container_type': ct,
                    'container_size': cs,
                    'line_items': [],
                    'shipping_line_id': None,
                    'commodity': None,
                    'payment_term': None,
                    'schedule_type': None
                })

        tfs_query = FclFreightRateEstimation.select(
            FclFreightRateEstimation.origin_location_id,
            FclFreightRateEstimation.origin_location_type,
            FclFreightRateEstimation.destination_location_id,
            FclFreightRateEstimation.destination_location_type,
            FclFreightRateEstimation.shipping_line_id,
            FclFreightRateEstimation.commodity,
            FclFreightRateEstimation.container_size,
            FclFreightRateEstimation.container_type,
            FclFreightRateEstimation.created_at,
            FclFreightRateEstimation.updated_at,
            FclFreightRateEstimation.schedule_type,
            FclFreightRateEstimation.payment_term,
            FclFreightRateEstimation.line_items,
            FclFreightRateEstimation.id,
            FclFreightRateEstimation.status
        ).where(
            FclFreightRateEstimation.origin_location_id == actual_transformation['origin_location_id'],
            FclFreightRateEstimation.destination_location_id == actual_transformation['destination_location_id'],
            FclFreightRateEstimation.container_type << container_types,
            FclFreightRateEstimation.container_size << container_sizes
        )

        already_created_tfs = jsonable_encoder(list(tfs_query.dicts())) or []

        already_created_tfs_hash = {}

        for act in already_created_tfs:
            key = '{}:{}:{}:{}:{}:{}'.format(
                act['origin_location_id'],
                act['origin_location_type'],
                act['destination_location_id'], 
                act['destination_location_type'],
                act['container_type'],
                act['container_size']
                )
            line_items = act['line_items'] or []

            derived = None

            for line_item in line_items:
                if 'derived' in line_item:
                    derived = act['id']

            already_created_tfs_hash[key] = derived

        not_created_tfs = []

        for pst in possible_transformations:
            key = '{}:{}:{}:{}:{}:{}'.format(
                pst['origin_location_id'],
                pst['origin_location_type'],
                pst['destination_location_id'], 
                pst['destination_location_type'],
                pst['container_type'],
                pst['container_size']
                )

            derived = already_created_tfs_hash.get(key)
            if key not in already_created_tfs_hash or derived:
                if derived:
                    pst['id'] = derived

                not_created_tfs.append(pst)
        
        return not_created_tfs
    
    def get_relative_price(self, actual_transformation: dict, related_transformation: dict, line_item:dict):
        related_container_type = str(related_transformation['container_type'])
        related_container_size = str(related_transformation['container_size'])
        actual_container_size = str(actual_transformation['container_size'])
        actual_container_type = str(actual_transformation['container_type'])

        container_size_factor = CONTAINER_SIZE_FACTORS[actual_container_size]
        container_type_factor = CONTAINR_TYPE_FACTORS[actual_container_type]
        standard_rate_factor = 1 / container_size_factor
        standard_rate_factor = standard_rate_factor / container_type_factor
        realted_csf = CONTAINER_SIZE_FACTORS[related_container_size]
        realted_ctf = CONTAINR_TYPE_FACTORS[related_container_type]

        price = line_item['average']
        std_dev = line_item['stand_dev']
        related_rate_average = price * standard_rate_factor * realted_csf * realted_ctf
        lower_limit = related_rate_average - 1 * std_dev # -1 sigma
        upper_limit = related_rate_average + 1 * std_dev # 1 sigma
        
        return {
            'code': line_item['code'],
            'currency': self.target_currency,
            'upper_limit': round(upper_limit),
            'lower_limit': round(lower_limit),
            'average': related_rate_average,
            'stand_dev': std_dev,
            'size': line_item['size'],
            'unit': line_item['unit'],
            'derived': actual_transformation['id']
        }

    
    def relative_price_to_add(self, actual_transformation: dict, related_transformation: dict):
        line_items = actual_transformation['line_items'] or []

        new_lineitems = []

        for line_item in line_items:
            related_lineitem = self.get_relative_price(actual_transformation, related_transformation, line_item)
            new_lineitems.append(related_lineitem)
        
        return new_lineitems

    def adjust_price_for_related_transformations(self, actual_transformation):
        container_sizes = ['20', '40', '40HC', '45HC']
        container_sizes.remove(actual_transformation['container_size']) 
        container_types = ['standard', 'refer', 'open_top', 'open_side', 'flat_rack', 'iso_tank'] 
        container_types.remove(actual_transformation['container_type'])  

        related_transformations_to_add = self.get_related_transformations_to_add(actual_transformation, container_sizes, container_types)

        for rtf in related_transformations_to_add:
            # Insert price element to transformations
            rtf['line_items'] = self.relative_price_to_add(actual_transformation, rtf)
            self.adjust_price_for_tranformation(affected_transformation=rtf, new=False, is_relative=True)


    
    
    def adjust_price_for_tranformation(self, affected_transformation, new: bool=False, is_relative: bool = False):
        from celery_worker import update_multiple_service_objects
        transformation_id = affected_transformation.get('id')
        if is_relative:
            adjusted_line_items = affected_transformation['line_items']
        else:
            adjusted_line_items = self.get_adjusted_line_items_to_add(affected_transformation, new)
        

        if len(adjusted_line_items) == 0:
            # Return If no line_items to create
            return
        
        if not transformation_id and new:
            tf = self.get_transformation(affected_transformation)
            if tf:
                transformation_id = tf['id']
 
        if transformation_id:
            transformation = FclFreightRateEstimation.update(
                line_items = adjusted_line_items,
                updated_at = datetime.now()
            ).where(
                FclFreightRateEstimation.id == transformation_id
            ).execute()

            data = {
                'data': {
                    'line_items': adjusted_line_items,
                    'actual_line_items': self.new_rate.get('line_items')
                },
                'object_id': transformation_id,
                'action_name': 'update',
                'source': 'system'
            }
            self.create_audits(data=data)
        else:
            payload = affected_transformation | {
                'line_items': adjusted_line_items,
                'actual_line_items': self.new_rate.get('line_items')
            }
            transformation = FclFreightRateEstimation.create(
                origin_location_id = payload['origin_location_id'],
                origin_location_type = payload['origin_location_type'],
                destination_location_id = payload['destination_location_id'],
                destination_location_type=payload['destination_location_type'],
                container_size =payload['container_size'],
                container_type=payload['container_type'],
                line_items=payload['line_items'],
                shipping_line_id=payload['shipping_line_id'],
                commodity=payload['commodity'],
                payment_term=payload['payment_term'],
                schedule_type=payload['schedule_type'],
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
        
        if not is_relative:
            actual_transformation = affected_transformation
            actual_transformation['line_items'] = adjusted_line_items
            try:
                self.adjust_price_for_related_transformations(actual_transformation=actual_transformation)
            except Exception as e:
                sentry_sdk.capture_exception(e)
        
        return True




    def set_dynamic_pricing(self):
        '''
          Main Function to set dynamic pricing bounds  
        '''  
        from celery_worker import transform_dynamic_pricing
        if self.new_rate['rate_type'] != 'market_place' or self.new_rate['mode'] == 'predicted' or (self.ff_mlo and self.new_rate["service_provider_id"] not in self.ff_mlo):
            return False
        
        affected_transformations = self.get_transformations_to_be_affected()

        new_transformations_to_add = self.get_transformations_to_be_added(affected_transformations)

        for affected_transformation in affected_transformations:
            if self.what_to_create[affected_transformation['origin_location_type']]:
                # self.adjust_price_for_tranformation(affected_transformation=affected_transformation, new=False)
                transform_dynamic_pricing.apply_async(kwargs={ 'new_rate': self.new_rate, 'current_validities': self.current_validities, 'affected_transformation': affected_transformation, 'new': False }, queue='low')
        
        for new_transformation in new_transformations_to_add:
            # self.adjust_price_for_tranformation(affected_transformation=new_transformation, new=True)
            transform_dynamic_pricing.apply_async(kwargs={ 'new_rate': self.new_rate, 'current_validities': self.current_validities, 'affected_transformation': new_transformation, 'new': True }, queue='low')
        
        return True
