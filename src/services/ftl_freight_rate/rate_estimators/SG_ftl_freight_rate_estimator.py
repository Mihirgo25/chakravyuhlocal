from services.ftl_freight_rate.models.ftl_freight_rate_rule_set import FtlFreightRateRuleSet
from configs.ftl_freight_rate_constants import SG_BASIC_CHARGE_LIST,ROUND_TRIP_CHARGE,HAZ_CLASSES,SINGAPORE_HAZARDOUS_RATE,SINGAPORE_REEFER_RATE

class SGFtlFreightRateEstimator:
    def __init__(self,origin_location_id,destination_location_id,location_data_mapping,truck_and_commodity_data,average_fuel_price,path_data):
        self.origin_location_id = origin_location_id
        self.destination_location_id  = destination_location_id
        self.location_data_mapping = location_data_mapping
        self.truck_and_commodity_data = truck_and_commodity_data
        self.average_fuel_price = average_fuel_price
        self.path_data = path_data

    def estimate(self):
        currency = 'SGD'
        total_path_distance = self.path_data['distance']
        truck_type = self.truck_and_commodity_data["truck_type"]
        truck_mileage = self.truck_and_commodity_data['mileage']
        truck_weight = self.truck_and_commodity_data['weight']
        basic_freight_charges = (self.average_fuel_price*total_path_distance)/truck_mileage

        applicable_rule_set = self.get_applicable_rule_set_country()
        for data in applicable_rule_set:
            if data['process_type'] in SG_BASIC_CHARGE_LIST:
                process_unit = data['process_unit']
                if data['process_type'] == 'distance_factor':
                    # distance
                    basic_freight_charges += (total_path_distance) * (float(data['process_value']))
                elif data['process_type'] == 'capacity_factor':
                    # capacity
                    basic_freight_charges += ((truck_weight) * float(data['process_value']))
                elif data['process_type'] == 'driver':
                    # driver
                    basic_freight_charges += float(data['process_value'])
                elif data['process_type'] == 'loading_charge':
                    # loading charges
                    basic_freight_charges += float(data['process_value'])

        if self.truck_and_commodity_data['commodity'] in HAZ_CLASSES:
            basic_freight_charges = SINGAPORE_HAZARDOUS_RATE*basic_freight_charges

        if self.truck_and_commodity_data['truck_body_type'] == 'reefer':
            basic_freight_charges = SINGAPORE_REEFER_RATE*basic_freight_charges

        if self.truck_and_commodity_data['trip_type'] == 'round_trip':
            basic_freight_charges += ROUND_TRIP_CHARGE*basic_freight_charges

        result = {}
        result['currency']  = currency
        result["base_rate"] = round(basic_freight_charges,4)
        result["distance"] = total_path_distance
        return result

    def get_applicable_rule_set_country(self):
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
