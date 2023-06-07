from fastapi.encoders import jsonable_encoder
from datetime import datetime
from micro_services.client import common
from services.chakravyuh.models.cost_booking_estimation import CostBookingEstimation
from services.chakravyuh.models.cost_booking_estimation_audit import CostBookingEstimationAudit

class FclBookingVyuh():
    def __init__(self,
                new_rate: dict = {}, 
                what_to_create: dict = {
                'seaport': True,
                'country': True,
                'trade': True
                }
            ):
        self.new_rate = jsonable_encoder(new_rate)
        self.target_currency = 'USD'
        self.what_to_create = what_to_create
    
    def create_audits(self, data= {}):
        CostBookingEstimationAudit.create(**data)
    
    def get_transformations_to_be_affected(self):
        price_estimations_query = CostBookingEstimation.select(
            CostBookingEstimation.origin_location_id,
            CostBookingEstimation.origin_location_type,
            CostBookingEstimation.destination_location_id,
            CostBookingEstimation.destination_location_type,
            CostBookingEstimation.shipping_line_id,
            CostBookingEstimation.commodity,
            CostBookingEstimation.container_size,
            CostBookingEstimation.container_type,
            CostBookingEstimation.created_at,
            CostBookingEstimation.updated_at,
            CostBookingEstimation.schedule_type,
            CostBookingEstimation.payment_term,
            CostBookingEstimation.line_items,
            CostBookingEstimation.id,
            CostBookingEstimation.status
        ).where(
            CostBookingEstimation.origin_location_id << self.new_rate['origin_location_ids'],
            CostBookingEstimation.destination_location_id << self.new_rate['destination_location_ids'],
            CostBookingEstimation.container_size == self.new_rate['container_size'],
            CostBookingEstimation.container_type == self.new_rate['container_type'],
            ((CostBookingEstimation.commodity.is_null(True)) | (CostBookingEstimation.commodity == self.new_rate['commodity'])),
            ((CostBookingEstimation.shipping_line_id.is_null(True)) | (CostBookingEstimation.shipping_line_id == self.new_rate['shipping_line_id'])),
            CostBookingEstimation.status == 'active'
        )

        price_estimations = jsonable_encoder(list(price_estimations_query.dicts()))
        return price_estimations
    
    def get_transformation(self, payload):
        created_tf = CostBookingEstimation.select(CostBookingEstimation.id).where(
                CostBookingEstimation.origin_location_id == payload['origin_location_id'],
                CostBookingEstimation.destination_location_id == payload['destination_location_id'],
                CostBookingEstimation.container_size == payload['container_size'],
                CostBookingEstimation.container_type == payload['container_type'],
                CostBookingEstimation.schedule_type.is_null(True),
                CostBookingEstimation.payment_term.is_null(True),
                CostBookingEstimation.commodity.is_null(True),
                CostBookingEstimation.shipping_line_id.is_null(True),
                CostBookingEstimation.status == 'active'
            ).limit(1)

        price_estimations = jsonable_encoder(list(created_tf.dicts()))
        if len(price_estimations):
            return price_estimations[0]
        return None
    
    def get_transformations_to_be_added(self,already_added_tranformations: list = []):
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
    
    
    def get_lower_and_upper_limit_for_transformation_line_item(self, line_item: dict, affected_transformation):
        
        line_item_code = line_item['code']

        all_prices=[]

        price=0
        for item in self.new_rate['line_items']:
            if item['code']=='BAS':
                price=item['price']
                
        if price>10000:
            price=price/float(self.new_rate['containers_count'])

        
        if line_item['currency']!=self.target_currency:
            price = common.get_money_exchange_for_fcl({"price": price, "from_currency": line_item['currency'], "to_currency": self.target_currency })['price']
        all_prices.append(price)


        size = len(all_prices)
        mean = sum(all_prices) / size
        variance = sum([((x - mean) ** 2) for x in all_prices]) / size
        std_dev = variance ** 0.5
        lower_limit = mean - 1 * std_dev # -1 sigma
        upper_limit = mean + 1 * std_dev # 1 sigma

        if line_item.get('size'):
            size+=line_item['size']
        
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
        exp_average = old_mean * 0.2 + new_mean * 0.8
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
            max_bas_price = None
            max_bas_index = None

            for i, d in enumerate(line_items):
                if d['code'] == 'BAS':
                    if max_bas_price is None or d['price'] > max_bas_price:
                        max_bas_price = d['price']
                        max_bas_index = i

            max_line_item=line_items[max_bas_index]
            line_items=[]
            line_items.append(max_line_item)
            

        for line_item in line_items:
            if line_item['code'] == 'BAS':
                new_line_item = self.get_lower_and_upper_limit_for_transformation_line_item(line_item, affected_transformation)
                new_line_item = self.new_sigma_values(line_item, new_line_item)
                print('sigma_value',new_line_item)
                new_line_items.append(new_line_item)

        return new_line_items
        
    
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
            transformation = CostBookingEstimation.update(
                line_items = adjusted_line_items,
                updated_at = datetime.now()
            ).where(
                CostBookingEstimation.id == transformation_id
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
            transformation = CostBookingEstimation.create(
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
        
        return True
    

    def set_dynamic_pricing(self):
        '''
          Main Function to set dynamic pricing bounds  
        '''  
        from celery_worker import adjust_cost_booking_dynamic_pricing

        affected_transformations = self.get_transformations_to_be_affected()
        
        new_transformations_to_add = self.get_transformations_to_be_added(affected_transformations)

        for affected_transformation in affected_transformations:
            if self.what_to_create[affected_transformation['origin_location_type']]:
                # self.adjust_price_for_tranformation(affected_transformation=affected_transformation, new=False)
                adjust_cost_booking_dynamic_pricing.apply_async(kwargs={ 'new_rate': self.new_rate,'affected_transformation': affected_transformation, 'new': False }, queue='low')
                
        for new_transformation in new_transformations_to_add:
            adjust_cost_booking_dynamic_pricing.apply_async(kwargs={ 'new_rate': self.new_rate, 'affected_transformation': new_transformation, 'new': True }, queue='low')
       
        return True