from peewee import *
from playhouse.postgres_ext import *
from services.trailer_freight_rates.models.trailer_freight_rate_estimator_constant import TrailerFreightRateCharges
from services.envision.interaction.get_haulage_freight_predicted_rate import fuel_consumption
from database.db_session import db
from micro_services.client import maps
from playhouse.shortcuts import model_to_dict
from libs.get_distance import get_distance
from configs.trailer_freight_rate_constants import *


class INTrailerRateEstimator():

    def __init__(self, *_, **__): pass

    def estimate(self):
        ''' 
        Primary Function to estimate india prices
        '''
        print('Estimating India rates')

        origin_location_id = self.origin_location_id
        destination_location_id = self.destination_location_id
        country_code = self.country_code
        container_size = self.container_size
        container_type = self.container_type
        containers_count = self.containers_count
        cargo_weight_per_container = self.cargo_weight_per_container

        input = {"filters":{"id":[origin_location_id, destination_location_id]}}
        data = maps.list_locations(input)
        if data:
            data = data["list"]
        for d in data:
            if d["id"] == origin_location_id:
                origin_location = (d["latitude"], d["longitude"])
            if d["id"] == destination_location_id:
                destination_location = (d["latitude"], d["longitude"])
        try:
            distance = get_distance(origin_location,destination_location)
        except:
            distance = 250
        # data = maps.get_distance_matrix_valhalla(input)

        transit_time = (distance//250) * 24
        if transit_time == 0:
            transit_time = 12
        distance = distance if distance > 100 else 100
        fuel_used = fuel_consumption(distance,cargo_weight_per_container)
        
        fuel_cost = fuel_used * DEFAULT_FUEL_PRICES[country_code] #use fuel charge with currency

        my_class = INTrailerRateEstimator(self)
        constants_cost = my_class.constants_cost(distance)
        total_cost = fuel_cost + constants_cost

        total_cost = my_class.variable_cost(total_cost, container_size, container_type, containers_count) 

        return {'list':[{
            'base_price' : total_cost,
            'currency' : "INR",
            'distance' : distance,
            'transit_time' : transit_time,
            'upper_limit' : cargo_weight_per_container}]
            }

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
            total_cost = total_cost * (containers_count-0.2)

        if container_type in ['refer', 'open_top', 'iso_tank', 'flat_rack', 'open_side']:
            total_cost = total_cost + (total_cost * 0.5)

        return total_cost