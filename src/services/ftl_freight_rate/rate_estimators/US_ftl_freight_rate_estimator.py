from configs.ftl_freight_rate_constants import BASIC_CHARGE_LIST,HAZ_CLASSES,ADDITIONAL_CHARGE,ROUND_TRIP_CHARGE,LOADING_UNLOADING_CHARGES_US,MINIMUM_APPLICABLE_CHARGE, KILOMETRE_TO_MILE
from services.ftl_freight_rate.models.ftl_freight_rate_rule_set import FtlFreightRateRuleSet
class USFtlFreightRateEstimator:
    def __init__(self,origin_location_id,destination_location_id,location_data_mapping,truck_and_commodity_data,average_fuel_price,path_data,country_info):
        self.origin_location_id = origin_location_id
        self.destination_location_id  = destination_location_id
        self.location_data_mapping = location_data_mapping
        self.truck_and_commodity_data = truck_and_commodity_data
        self.average_fuel_price = average_fuel_price
        self.path_data = path_data
        self.country_info = country_info

    def estimate(self):
        currency = self.country_info.get('currency_code')
        country_code = self.country_info.get('country_code')
        total_path_distance = self.path_data['distance']*KILOMETRE_TO_MILE
        truck_mileage = self.truck_and_commodity_data['mileage']
        basic_freight_charges = (self.average_fuel_price*total_path_distance)/truck_mileage
        applicable_rule_set = self.get_applicable_rule_set()

        for data in applicable_rule_set:
            if data['process_type'] in BASIC_CHARGE_LIST[country_code]:
                process_unit = data['process_unit']
                if data['process_type'] == 'driver':
                    basic_freight_charges += (float(data['process_value'])*total_path_distance)
                else:
                    basic_freight_charges += (float(data['process_value'])*(total_path_distance))
        if self.truck_and_commodity_data['commodity'] in HAZ_CLASSES or self.truck_and_commodity_data['truck_body_type'] == 'reefer':
            basic_freight_charges += ADDITIONAL_CHARGE*basic_freight_charges
        weight = self.truck_and_commodity_data['weight']
        basic_freight_charges += weight*LOADING_UNLOADING_CHARGES_US

        if self.truck_and_commodity_data['trip_type'] == 'round_trip':
            basic_freight_charges += ROUND_TRIP_CHARGE*basic_freight_charges

        result = {}
        result['currency']  = currency
        result["base_rate"] = round(basic_freight_charges,4)
        result["distance"] = total_path_distance
        return result


    def get_applicable_rule_set(self):
        truck_type = self.truck_and_commodity_data["truck_type"]
        location_ids = list(set([
            self.location_data_mapping[self.origin_location_id]['country_id'],
            self.location_data_mapping[self.destination_location_id]['country_id']
            ]))

        ftl_freight_rate_rule_set = FtlFreightRateRuleSet.select(
            FtlFreightRateRuleSet.process_unit,
            FtlFreightRateRuleSet.process_type,
            FtlFreightRateRuleSet.process_value,
            FtlFreightRateRuleSet.process_currency
        ).where(
            FtlFreightRateRuleSet.location_id << (location_ids),
            FtlFreightRateRuleSet.location_type == "country",
            FtlFreightRateRuleSet.truck_type == truck_type,
            FtlFreightRateRuleSet.status == 'active'
        )
        final_data = list(ftl_freight_rate_rule_set.dicts())
        return final_data
