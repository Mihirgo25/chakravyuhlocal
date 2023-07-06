from configs.ftl_freight_rate_constants import (
    BASIC_CHARGE_LIST,
    HAZ_CLASSES,
    ADDITIONAL_CHARGE,
    ROUND_TRIP_CHARGE,
    LOADING_UNLOADING_CHARGES,
    MINIMUM_APPLICABLE_CHARGE,
    TRUCK_CAPACITY_RATE_FACTOR,
    DISTANCE_RATE_FACTOR,
    CLOSED_BODY_CHARGES_FOR_7,
    CLOSED_BODY_CHARGES_FOR_14,
)
from services.ftl_freight_rate.models.ftl_freight_rate_rule_set import (
    FtlFreightRateRuleSet,
)


class INFtlFreightRateEstimator:
    def __init__(
        self,
        origin_location_id,
        destination_location_id,
        location_data_mapping,
        truck_and_commodity_data,
        average_fuel_price,
        path_data,
        country_info
    ):
        self.origin_location_id = origin_location_id
        self.destination_location_id = destination_location_id
        self.location_data_mapping = location_data_mapping
        self.truck_and_commodity_data = truck_and_commodity_data
        self.average_fuel_price = average_fuel_price
        self.path_data = path_data
        self.country_info = country_info

    def estimate(self):
        currency = self.country_info.get('currency_code')
        country_code = self.country_info.get('country_code')
        total_path_distance = self.path_data["distance"]
        truck_mileage = self.truck_and_commodity_data["mileage"]

        basic_freight_charges = (
            self.average_fuel_price * total_path_distance
        ) / truck_mileage

        additional_charges = 0
        applicable_rule_set = self.get_applicable_rule_set()
        for data in applicable_rule_set:
            if data["process_type"] in BASIC_CHARGE_LIST[country_code]:
                additional_charges += float(data["process_value"])
        truck_capacity = self.truck_and_commodity_data["weight"]

        rate_factor_for_distance = 1
        MAX_LIMIT = "55"
        for truck_capacity_limit, rate_factor in TRUCK_CAPACITY_RATE_FACTOR.items():
            if truck_capacity > 39:
                rate_factor_for_distance = TRUCK_CAPACITY_RATE_FACTOR[MAX_LIMIT]
                break
            if truck_capacity <= float(truck_capacity_limit):
                rate_factor_for_distance = rate_factor
                break

        basic_freight_charges += (
            rate_factor_for_distance * additional_charges * total_path_distance
        )

        if self.truck_and_commodity_data["truck_body_type"] == "closed":
            if truck_capacity == 7.5:
                basic_freight_charges = (
                    basic_freight_charges * CLOSED_BODY_CHARGES_FOR_7
                )
            if truck_capacity > 14:
                basic_freight_charges = (
                    basic_freight_charges * CLOSED_BODY_CHARGES_FOR_14
                )

        distance_factor_key_based_on_truck_capacity = (
            1 if truck_capacity / 14 >= 1 else 0
        )
        distance_factor_data = None
        for distance_factor in DISTANCE_RATE_FACTOR[
            distance_factor_key_based_on_truck_capacity
        ]:
            if (
                total_path_distance > distance_factor["lower_limit"]
                and total_path_distance <= distance_factor["upper_limit"]
            ):
                distance_factor_data = distance_factor
                break

        if distance_factor_data is not None:
            if distance_factor_data.get("linear_decreasing"):
                distance_range_factor = total_path_distance * distance_factor_data.get(
                    "rate_factor"
                ) + distance_factor_data.get("rate_bar")
                basic_freight_charges = distance_range_factor * basic_freight_charges
            else:
                basic_freight_charges = (
                    distance_factor_data.get("rate_factor") * basic_freight_charges
                )

        if (
            self.truck_and_commodity_data["commodity"] in HAZ_CLASSES
            or self.truck_and_commodity_data["truck_body_type"] == "reefer"
        ):
            basic_freight_charges += ADDITIONAL_CHARGE * basic_freight_charges
        
        basic_freight_charges += truck_capacity * LOADING_UNLOADING_CHARGES
        if self.truck_and_commodity_data["trip_type"] == "round_trip":
            basic_freight_charges += ROUND_TRIP_CHARGE * basic_freight_charges
            
        result = {}
        result["currency"] = currency
        result["base_rate"] = round(basic_freight_charges, 4)
        result["distance"] = total_path_distance
        return result

    def get_applicable_rule_set(self):
        truck_type = self.truck_and_commodity_data["truck_type"]
        location_ids = list(
            set(
                [
                    self.location_data_mapping[self.origin_location_id]["country_id"],
                    self.location_data_mapping[self.destination_location_id][
                        "country_id"
                    ],
                ]
            )
        )
        ftl_freight_rate_rule_set = FtlFreightRateRuleSet.select(
            FtlFreightRateRuleSet.process_unit,
            FtlFreightRateRuleSet.process_type,
            FtlFreightRateRuleSet.process_value,
            FtlFreightRateRuleSet.process_currency,
        ).where(
            FtlFreightRateRuleSet.location_id << (location_ids),
            FtlFreightRateRuleSet.location_type == "country",
            FtlFreightRateRuleSet.truck_type == truck_type,
            FtlFreightRateRuleSet.status == "active",
        )
        final_data = list(ftl_freight_rate_rule_set.dicts())
        return final_data
