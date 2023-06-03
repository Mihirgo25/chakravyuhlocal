from peewee import *
from playhouse.postgres_ext import *
from services.trailer_freight_rates.models.trailer_freight_rate_estimator_constant import TrailerFreightRateCharges
from services.envision.interaction.get_haulage_freight_predicted_rate import fuel_consumption
from database.db_session import db
from micro_services.client import maps
from playhouse.shortcuts import model_to_dict
from configs.trailer_freight_rate_constants import *
from services.trailer_freight_rates.helpers.trailer_freight_rate_estimator_helper import get_estimated_distance


class INTrailerRateEstimator():

    def __init__(self, origin_location_id, destination_location_id, country_code):
        self.origin_location_id = origin_location_id
        self.destination_location_id = destination_location_id
        self.country_code = country_code

    def constants_cost(self,distance):
        constants = TrailerFreightRateCharges.select().where(
                    (TrailerFreightRateCharges.country_code == "IN"),
                    (TrailerFreightRateCharges.status == 'active')
                    ).order_by(TrailerFreightRateCharges.created_at.desc()).first()
        constants_data = model_to_dict(constants)

        handling_rate = constants_data.get('handling')
        nh_toll_rate = constants_data.get('nh_toll')
        tyre_rate = constants_data.get('tyre')
        driver_rate = constants_data.get('driver')
        document_rate = constants_data.get('document')
        maintanance_rate = constants_data.get('maintanance')
        misc_rate = constants_data.get('misc')

        constants_cost = (handling_rate + nh_toll_rate + tyre_rate + driver_rate + document_rate + maintanance_rate + misc_rate) * distance
        return constants_cost

    def variable_cost(self, total_cost, container_size, container_type, containers_count):
        total_cost = total_cost * CONTAINER_SIZE_FACTORS[container_size]

        if containers_count > 1:
            total_cost = (total_cost * (containers_count-CONTAINER_COUNT_FACTOR))/containers_count

        total_cost = total_cost * CONTAINR_TYPE_FACTORS[container_type]

        return total_cost

    def IN_estimate(self, container_size, container_type, containers_count, cargo_weight_per_container, trip_type):
        ''' 
        Primary Function to estimate india prices
        '''
        print('Estimating India rates')

        origin_location_id = self.origin_location_id
        destination_location_id = self.destination_location_id
        country_code = self.country_code
        trip_type = trip_type if trip_type is not None else DEFAULT_TRIP_TYPE

        distance = get_estimated_distance(origin_location_id, destination_location_id)
        distance = distance if distance > 100 else 100
        # data = maps.get_distance_matrix_valhalla(input)

        transit_time = (distance//250) * 24
        if transit_time == 0:
            transit_time = 10

        fuel_used = fuel_consumption(distance,cargo_weight_per_container)
        
        fuel_cost = fuel_used * DEFAULT_FUEL_PRICES["INR"] #use fuel charge with currency

        constants_cost = self.constants_cost(distance)
        total_cost = fuel_cost + constants_cost

        total_cost = self.variable_cost(total_cost, container_size, container_type, containers_count)

        if trip_type == 'round_trip':
            total_cost = total_cost * ROUND_TRIP_FACTOR

        return {'list':[{
            'base_price' : total_cost,
            'currency' : "INR",
            'distance' : distance,
            'transit_time' : transit_time,
            'upper_limit' : cargo_weight_per_container,
            'trip_type' : trip_type}]
            }