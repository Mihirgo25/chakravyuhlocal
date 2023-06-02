from services.ftl_freight_rate.models.ftl_freight_rate_rule_set import FtlFreightRateRuleSet

class EUFtlFreightRateEstimator:
    def __init__(self,origin_location_id,destination_location_id,location_data_mapping,truck_and_commodity_data,average_fuel_price,path_data):
        self.origin_location_id = origin_location_id
        self.destination_location_id  = destination_location_id
        self.location_data_mapping = location_data_mapping
        self.truck_and_commodity_data = truck_and_commodity_data
        self.average_fuel_price = average_fuel_price
        self.path_data = path_data

    def estimate(self):
        pass
