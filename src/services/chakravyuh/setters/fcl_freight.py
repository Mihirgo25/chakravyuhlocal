from fastapi.encoders import jsonable_encoder
from datetime import datetime
from micro_services.client import common
from services.chakravyuh.models.fcl_freight_rate_estimation import FclFreightRateEstimation
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.chakravyuh.models.fcl_freight_rate_estimation_audit import FclFreightRateEstimationAudit

class FclFreightVyuh():
    def __init__(self, new_rate: dict = {}, current_validities: dict = []):
        self.new_rate = jsonable_encoder(new_rate)
        self.current_validities = current_validities
        self.target_currency = 'USD'
    
    def create_audits(self, data= {}):
        FclFreightRateEstimationAudit.create(**data)
    
    def get_transformations_to_be_affected(self):
        price_estimations_query = FclFreightRateEstimation.select().where(
            FclFreightRateEstimation.origin_location_id << self.new_rate['origin_location_ids'],
            FclFreightRateEstimation.destination_location_id << self.new_rate['destination_location_ids'],
            FclFreightRateEstimation.container_size == self.new_rate['container_size'],
            FclFreightRateEstimation.container_type == self.new_rate['container_type'],
            ((FclFreightRateEstimation.schedule_type.is_null(True)) | (FclFreightRateEstimation.schedule_type == self.new_rate['schedule_type'])),
            ((FclFreightRateEstimation.payment_term.is_null(True)) | (FclFreightRateEstimation.payment_term == self.new_rate['payment_term'])),
            ((FclFreightRateEstimation.commodity.is_null(True)) | (FclFreightRateEstimation.commodity == self.new_rate['commodity'])),
            ((FclFreightRateEstimation.shipping_line_id.is_null(True)) | (FclFreightRateEstimation.shipping_line_id == self.new_rate['shipping_line_id']))
        )

        price_estimations = jsonable_encoder(list(price_estimations_query.dicts()))
        return price_estimations
    
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
            FclFreightRate.container_size == affected_transformation['container_size'],
            FclFreightRate.container_type == affected_transformation['container_type'],
            ~FclFreightRate.rate_not_available_entry,
            FclFreightRate.last_rate_available_date >= current_date
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
                converted_price = common.get_money_exchange_for_fcl({"price": line_item['price'], "from_currency": matching_lineitem['currency'], "to_currency": self.target_currency })['price']
            
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
    
    def get_adjusted_line_items_to_add(self, affected_transformation: dict = {}, new:bool = False):
        line_items = affected_transformation['line_items'] or []
        new_line_items = []

        if new:
            line_items = self.new_rate['line_items'] or []

        for line_item in line_items:
            if line_item['code'] == 'BAS':
                new_line_item = self.get_lower_and_upper_limit_for_transformation_line_item(line_item, affected_transformation)
                new_line_items.append(new_line_item)

        return new_line_items
    
    
    def adjust_price_for_tranformation(self, affected_transformation, new: bool=False):
        transformation_id = affected_transformation.get('id')
        adjusted_line_items = self.get_adjusted_line_items_to_add(affected_transformation, new)

        if len(adjusted_line_items) == 0:
            # Return If no line_items to create
            return
        
        if transformation_id:
            transformation = FclFreightRateEstimation.update(
                line_items = adjusted_line_items
            ).where(
                FclFreightRateEstimation.id == transformation_id
            ).execute()

            data = {
                'data': {
                    'line_items': adjusted_line_items,
                },
                'object_id': transformation_id,
                'action_name': 'update',
                'source': 'system'
            }
            self.create_audits(data=data)
            return transformation
        else:
            payload = affected_transformation | {
                'line_items': adjusted_line_items
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
                schedule_type=payload['schedule_type']
            )
            data = {
                'data': payload,
                'object_id': transformation.id,
                'action_name': 'create',
                'source': 'system'
            }
            self.create_audits(data=data)
            return transformation


    def set_dynamic_pricing(self):
        '''
            
        '''     
        if self.new_rate['mode'] == 'predicted':
            return False
        
        affected_transformations = self.get_transformations_to_be_affected()

        new_transformations_to_add = self.get_transformations_to_be_added(affected_transformations)

        for affected_transformation in affected_transformations:
            self.adjust_price_for_tranformation(affected_transformation)
        
        for new_transformation in new_transformations_to_add:
            self.adjust_price_for_tranformation(new_transformation, True)


        return True
