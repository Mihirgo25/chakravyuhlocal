from configs.ftl_freight_rate_constants import BASIC_CHARGE_LIST,HAZ_CLASSES,ADDITIONAL_CHARGE,ROUND_TRIP_CHARGE,LOADING_UNLOADING_CHARGES_CN,MINIMUM_APPLICABLE_CHARGE_CN
from services.ftl_freight_rate.models.ftl_freight_rate_rule_set import FtlFreightRateRuleSet
class CNFtlFreightRateEstimator:
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
        total_path_distance = self.path_data['distance']
        truck_mileage = self.truck_and_commodity_data['mileage']
        weight = self.truck_and_commodity_data['weight']
        vehicle_weight= self.truck_and_commodity_data['vehicle_weight']
        no_of_wheels= self.truck_and_commodity_data['no_of_wheels'] or self.get_no_of_wheels(vehicle_weight)

        basic_freight_charges = (self.average_fuel_price*total_path_distance)/truck_mileage

        applicable_rule_set = self.get_applicable_rule_set()
        for data in applicable_rule_set:
            if data['process_type'] in BASIC_CHARGE_LIST[country_code]:
                if data['process_type'] == 'driver' or data['process_type'] == 'emi':
                    basic_freight_charges += (float(data['process_value'])*self.get_driver_charges_factor(total_path_distance))

                elif data['process_type'] == 'toll':
                    basic_freight_charges += (float(data['process_value'])*self.get_toll_charges_factor_CN(vehicle_weight, total_path_distance))
            
                elif data['process_type'] == 'tyre' or data['process_type'] == 'maintenance':
                    basic_freight_charges += (float(data['process_value'])*no_of_wheels*total_path_distance)

                else:
                    basic_freight_charges += (float(data['process_value'])*(total_path_distance))


        if self.truck_and_commodity_data['trip_type'] == 'round_trip':
            basic_freight_charges += ROUND_TRIP_CHARGE*basic_freight_charges
        if self.truck_and_commodity_data['commodity'] in HAZ_CLASSES or self.truck_and_commodity_data['truck_body_type'] == 'reefer':
            basic_freight_charges += ADDITIONAL_CHARGE*basic_freight_charges
            
        basic_freight_charges += weight*LOADING_UNLOADING_CHARGES_CN

        result = {}
        result['currency']  = currency
        result["base_rate"] = round(basic_freight_charges,4)
        result["distance"] = total_path_distance
        return result
    
    def get_no_of_wheels(vehicle_weight):
        if vehicle_weight < 2:
            return 4
        elif vehicle_weight < 10:
            return 6
        elif vehicle_weight < 18:
            return 8
        elif vehicle_weight < 25:
            return 10
        return 12
    
    def get_driver_charges_factor(self,total_distance):
        if total_distance <= 300:
            return MINIMUM_APPLICABLE_CHARGE_CN
        return total_distance
    
    def get_toll_charges_factor_CN(self,vehicle_weight,total_distance):
        if vehicle_weight <= 5:
            return 5*total_distance
        elif vehicle_weight <=10:
            return 1.25*vehicle_weight*total_distance
        elif vehicle_weight <=20:
            return ((1.1*10)+(vehicle_weight-10)*(7/6-(vehicle_weight/60)))*total_distance
        elif vehicle_weight <=40:
            return (10+(vehicle_weight-10)*(370/300-7*(vehicle_weight/300)))*total_distance
        
        return (10+(vehicle_weight-10)*0.3)*total_distance

    def get_applicable_rule_set(self):
        truck_type = self.truck_and_commodity_data["truck_type"]
        location_ids = list(set([self.location_data_mapping[self.origin_location_id]['country_id'],self.location_data_mapping[self.destination_location_id]['country_id']]))
        ftl_freight_rate_rule_set = FtlFreightRateRuleSet.select(FtlFreightRateRuleSet.process_unit,FtlFreightRateRuleSet.process_type,FtlFreightRateRuleSet.process_value,FtlFreightRateRuleSet.process_currency).where(
                FtlFreightRateRuleSet.location_id << (location_ids),
                FtlFreightRateRuleSet.location_type == "country",
                FtlFreightRateRuleSet.truck_type == truck_type,
                FtlFreightRateRuleSet.status == 'active'
            )
        final_data = list(ftl_freight_rate_rule_set.dicts())
        return final_data


