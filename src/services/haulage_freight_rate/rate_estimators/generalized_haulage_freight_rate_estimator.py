
from fastapi import HTTPException

DEFAULT_ENVIRONMENT_PROTECTION_INDEX = 0.00543
DEFAULT_CLIMATE_CHANGE_FEE_INDEX = 0.00116
DEFAULT_NOISE_POLLUTION_FEE_INDEX = 0.00053
DEFAULT_INDIRECT_POLLUTION_FEE_INDEX = 0.00742
DEFAULT_POLLUTION_INDEX = 0.01454
DEFAULT_SAFTEY_INDEX = 0.97
DEFAULT_WEIGHT_INDEX = 0.25


class GeneralizedHaulageFreightRateEstimator:
    def __init__(self, *_, **__):
        pass

    def estimate(self):
        """
        Primary Function to estimate generalized prices
        """

        """
        total_cost_of_goods_trasport = basic_cost(c1) + railway_construction_fund(c2) + electrification_surcharges + pick_up + delivery_charge + loading_charges + miscellaneous_charges
        """
        total_cost_of_goods_trasport = cost_of_goods_transport + loading_charges + miscellaneous_charges
        time_value_of_goods = time_of_goods_transport + order_acceptence_waiting_time + transportation_time + loading_time_of_diffrent_modes_of_transportation

        """
        generalized_cost_of_railway_environmental_protection = 
        """
        generalized_cost_of_environmental_protection = direct_pollution_cost + indirect_pollution_cost 
        safety_index = cargo_damage + cargo_difference
        weight_of_economy = ''
        timliness_index = ''
        environmental_protection_index = ''
        transportation_time = ''
        volume_of_goods_traffic = ''
        """
        generalized cost = ( (weight_of_economy) * (total_cost_of_goods_trasport) + (timliness_index) * (time_value_of_goods) * (transportation_time) * (volume_of_goods_traffic) + (environmental_protection_index) * (generalized_cost_of_environmental_protection) ) // safety_index
        """
        generalized_cost = ( (weight_of_economy) * (total_cost_of_goods_trasport) + (timliness_index) * (time_value_of_goods) * (transportation_time) * (volume_of_goods_traffic) + (environmental_protection_index) * (generalized_cost_of_environmental_protection) ) // safety_index

        raise HTTPException(status_code=400, detail="rates not present")
