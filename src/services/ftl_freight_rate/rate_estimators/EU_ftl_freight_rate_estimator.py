from services.ftl_freight_rate.models.ftl_freight_rate_rule_set import FtlFreightRateRuleSet
from configs.ftl_freight_rate_constants import EU_BASIC_CHARGE_LIST

class EUFtlFreightRateEstimator:
    def __init__(self,origin_location_id,destination_location_id,location_data_mapping,truck_and_commodity_data,average_fuel_price,path_data):
        self.origin_location_id = origin_location_id
        self.destination_location_id  = destination_location_id
        self.location_data_mapping = location_data_mapping
        self.truck_and_commodity_data = truck_and_commodity_data
        self.average_fuel_price = average_fuel_price
        self.path_data = path_data

    def estimate(self):
        currency = 'USD'
        total_path_distance = self.path_data['distance']
        trip_duration = self.path_data['time']
        truck_mileage = self.truck_and_commodity_data['mileage']
        truck_weight = self.truck_and_commodity_data['weight']
        basic_freight_charges = 0

        applicable_rule_set = self.get_applicable_rule_set()
        for data in applicable_rule_set:
            if data['process_type'] in EU_BASIC_CHARGE_LIST:
                process_unit = data['process_unit']
                if data['process_type'] == 'distance_factor':
                    # distance
                    basic_freight_charges += (total_path_distance +  self.average_fuel_price/truck_mileage) * (float(data['process_value']))
                elif data['process_type'] == 'time_factor':
                    # time
                    basic_freight_charges += (float(data['process_value'])*(trip_duration))
                elif data['process_type'] == 'capacity_factor':
                    # capacity
                    basic_freight_charges += (float(data['process_value'])*(truck_weight))
                elif data['process_type'] == 'constant':
                    # constants
                    basic_freight_charges += float(data['process_value'])

        result = {}
        result['currency']  = currency
        result["base_rate"] = round(basic_freight_charges,4)
        result["distance"] = total_path_distance
        result["trip_duration"] = trip_duration
        return result


    def get_applicable_rule_set(self):
        truck_type = self.truck_and_commodity_data["truck_type"]
        location_ids = list(set([self.location_data_mapping[self.origin_location_id]['continent_id'],self.location_data_mapping[self.destination_location_id]['continent_id']]))
        ftl_freight_rate_rule_set = FtlFreightRateRuleSet.select(FtlFreightRateRuleSet.process_unit,FtlFreightRateRuleSet.process_type,FtlFreightRateRuleSet.process_value,FtlFreightRateRuleSet.process_currency).where(
                FtlFreightRateRuleSet.location_id << (location_ids),
                FtlFreightRateRuleSet.location_type == "continent",
                FtlFreightRateRuleSet.truck_type == truck_type,
                FtlFreightRateRuleSet.status == 'active'
            )
        final_data = list(ftl_freight_rate_rule_set.dicts())
        return final_data
