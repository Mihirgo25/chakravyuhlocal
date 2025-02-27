from services.ftl_freight_rate.models.ftl_freight_rate_rule_set import FtlFreightRateRuleSet
from configs.ftl_freight_rate_constants import BASIC_CHARGE_LIST, DEFAULT_TOLL_PRICE_EU, ROUND_TRIP_CHARGE, HAZ_CLASSES, EUROPE_HAZARDOUS_RATE, EUROPE_REEFER_RATE, AVERAGE_SPEEDS

class EUFtlFreightRateEstimator:
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
        truck_type = self.truck_and_commodity_data["truck_type"]
        trip_duration = total_path_distance/AVERAGE_SPEEDS[truck_type]
        truck_mileage = self.truck_and_commodity_data['mileage']
        truck_weight = self.truck_and_commodity_data['weight']
        basic_freight_charges = 0

        applicable_rule_set = self.get_applicable_rule_set_continent()
        for data in applicable_rule_set:
            if data['process_type'] in BASIC_CHARGE_LIST[country_code]:
                process_unit = data['process_unit']
                if data['process_type'] == 'distance_factor':
                    # distance
                    fuel_factor = self.get_fuel_factor(truck_mileage)
                    toll_factor = self.get_toll_factor()
                    basic_freight_charges += (total_path_distance +  fuel_factor + toll_factor) * (float(data['process_value']))
                elif data['process_type'] == 'time_factor':
                    # time
                    basic_freight_charges += ((trip_duration) * float(data['process_value']))
                elif data['process_type'] == 'capacity_factor':
                    # capacity
                    basic_freight_charges += ((truck_weight) * float(data['process_value']))
                elif data['process_type'] == 'loading_charge':
                    # loading charges
                    basic_freight_charges += float(data['process_value'])

        if self.truck_and_commodity_data['commodity'] in HAZ_CLASSES:
            basic_freight_charges = EUROPE_HAZARDOUS_RATE*basic_freight_charges

        if self.truck_and_commodity_data['truck_body_type'] == 'reefer':
            basic_freight_charges = EUROPE_REEFER_RATE*basic_freight_charges

        if self.truck_and_commodity_data['trip_type'] == 'round_trip':
            basic_freight_charges += ROUND_TRIP_CHARGE*basic_freight_charges

        result = {}
        result['currency']  = currency
        result["base_rate"] = round(basic_freight_charges,4)
        result["distance"] = total_path_distance
        result["trip_duration"] = trip_duration
        return result


    def get_applicable_rule_set_continent(self):
        truck_type = self.truck_and_commodity_data["truck_type"]
        location_ids = list(set([
            self.location_data_mapping[self.origin_location_id]['continent_id'],
            self.location_data_mapping[self.destination_location_id]['continent_id']
            ]))

        ftl_freight_rate_rule_set = FtlFreightRateRuleSet.select(
            FtlFreightRateRuleSet.process_unit,
            FtlFreightRateRuleSet.process_type,
            FtlFreightRateRuleSet.process_value,
            FtlFreightRateRuleSet.process_currency
        ).where(
            FtlFreightRateRuleSet.location_id << (location_ids),
            FtlFreightRateRuleSet.location_type == "continent",
            FtlFreightRateRuleSet.truck_type == truck_type,
            FtlFreightRateRuleSet.status == 'active'
        )
        final_data = list(ftl_freight_rate_rule_set.dicts())
        return final_data

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


    def get_fuel_factor(self, truck_mileage):
        return self.average_fuel_price/truck_mileage

    def get_toll_factor(self):
        country_rule_set = self.get_applicable_rule_set_country()
        if not country_rule_set:
            return DEFAULT_TOLL_PRICE_EU

        toll_value = 0
        is_origin_destination_rule_present = len(country_rule_set) == 2
        for data in country_rule_set:
            toll_value += float(data['process_value'])

        if not is_origin_destination_rule_present:
            toll_value += DEFAULT_TOLL_PRICE_EU

        toll_value = toll_value / 2
        return toll_value
