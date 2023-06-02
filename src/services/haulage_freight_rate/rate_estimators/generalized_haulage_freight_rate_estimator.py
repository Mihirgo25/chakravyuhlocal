from fastapi import HTTPException

from configs.haulage_freight_rate_constants import (
    CONTAINER_SIZE_FACTORS,
    DEFAULT_MAX_WEIGHT_LIMIT,
    VIETNAMESE_INFLATION_FACTOR,
    USD_TO_VND,
    CONTAINER_HANDLING_CHARGES,
    DEFAULT_ENVIRONMENT_PROTECTION_INDEX,
    DEFAULT_CLIMATE_CHANGE_FEE_INDEX,
    DEFAULT_NOISE_POLLUTION_FEE_INDEX,
    DEFAULT_INDIRECT_POLLUTION_FEE_INDEX,
    DEFAULT_POLLUTION_INDEX,
    DEFAULT_WEIGHT_INDEX,
    AVERAGE_ENERGY_CONSUMPTION
)
from services.haulage_freight_rate.models.energy_data import EnergyData


class GeneralizedHaulageFreightRateEstimator:
    def __init__(
        self,
        query,
        commodity,
        load_type,
        containers_count,
        distance,
        container_type,
        cargo_weight_per_container,
        permissable_carrying_capacity,
        container_size,
        transit_time,
        country_code
    ):
        self.query = query
        self.commodity = commodity
        self.load_type = load_type
        self.containers_count = containers_count
        self.distance = distance
        self.container_type = container_type
        self.cargo_weight_per_container = cargo_weight_per_container
        self.permissable_carrying_capacity = permissable_carrying_capacity
        self.container_size = container_size
        self.transit_time = transit_time
        self.country_code = country_code

    def estimate(self):
        """
        Primary Function to estimate generalized prices
        """
        final_price = self.generate_generalized_rates(
            query=self.query,
            commodity=self.commodity,
            load_type=self.load_type,
            containers_count=self.containers_count,
            location_pair_distance=self.distance,
            container_type=self.container_type,
            cargo_weight_per_container=self.cargo_weight_per_container,
            permissable_carrying_capacity=self.permissable_carrying_capacity,
            container_size=self.container_size,
            transit_time=self.transit_time,
            country_code=self.country_code
        )
        if not final_price:
            raise HTTPException(status_code=400, detail="rates not present")
        return final_price

    def generate_generalized_rates(
        self,
        query,
        commodity,
        load_type,
        containers_count,
        location_pair_distance,
        container_type,
        cargo_weight_per_container,
        permissable_carrying_capacity,
        container_size,
        transit_time,
        country_code
    ):
        """
        total_cost_of_goods_trasport = basic_cost(c1) + railway_construction_fund(c2) + electrification_surcharges + pick_up + delivery_charge + loading_charges + miscellaneous_charges
        """ 
        energy_consumption = location_pair_distance * AVERAGE_ENERGY_CONSUMPTION * cargo_weight_per_container
        energy_cost = EnergyData.select(EnergyData.fuel_price).where(EnergyData.country_code == country_code)
        if energy_cost.count()==0:
            raise HTTPException(status_code=400, detail="rates not present")
        energy_price = list(energy_cost.dicta())[0]
        cost_of_goods_transport = energy_consumption * energy_price
        loading_charges = float(CONTAINER_HANDLING_CHARGES[container_size]['stuffed']['warehouse_to_automobile'])
        miscellaneous_charges = 10
        total_cost_of_goods_trasport = (
            cost_of_goods_transport + loading_charges + miscellaneous_charges
        )
        
        """time_value_of_goods = (
            time_of_goods_transport
            + order_acceptence_waiting_time
            + transportation_time
            + loading_time_of_diffrent_modes_of_transportation
        )
        """
        """
        generalized_cost_of_railway_environmental_protection = 
        """
        # generalized_cost_of_environmental_protection = (
        #     direct_pollution_cost + indirect_pollution_cost
        # )
        # safety_index = cargo_damage + cargo_difference
        # weight_of_economy = ""
        # timliness_index = ""
        # environmental_protection_index = ""
        # transportation_time = ""
        # volume_of_goods_traffic = ""
        """
        generalized cost = ( (weight_of_economy) * (total_cost_of_goods_trasport) + (timliness_index) * (time_value_of_goods) * (transportation_time) * (volume_of_goods_traffic) + (environmental_protection_index) * (generalized_cost_of_environmental_protection) ) // safety_index
        """
        # generalized_cost = (
        #     (weight_of_economy) * (total_cost_of_goods_trasport)
        #     + (timliness_index)
        #     * (time_value_of_goods)
        #     * (transportation_time)
        #     * (volume_of_goods_traffic)
        #     + (environmental_protection_index)
        #     * (generalized_cost_of_environmental_protection)
        # ) // safety_index

        raise HTTPException(status_code=400, detail="rates not present")
