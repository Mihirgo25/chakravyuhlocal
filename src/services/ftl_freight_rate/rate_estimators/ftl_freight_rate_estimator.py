from services.ftl_freight_rate.rate_estimators.IN_ftl_freight_rate_estimator import INFtlFreightRateEstimator
from services.ftl_freight_rate.models.fuel_data import FuelData
from services.ftl_freight_rate.helpers.ftl_freight_rate_helpers import get_path_data
class FtlFreightEstimator:
    def __init__(self, origin_location_id, destination_location_id,location_data_mapping,truck_and_commodity_data):
        self.origin_location_id = origin_location_id
        self.destination_location_id = destination_location_id
        self.location_data_mapping = location_data_mapping
        self.truck_and_commodity_data = truck_and_commodity_data

    def estimate(self):
        path_data = self.get_path_from_valhala()
        location_data = path_data['location_details']
        is_location_data_from_valhala = path_data['is_valhala']
        country_category  = self.get_country_code()
        if country_category == 'IN':
            average_fuel_price = self.get_average_fuel_price(is_location_data_from_valhala,location_data,'diesel','INR')
            estimator = INFtlFreightRateEstimator(self.origin_location_id, self.destination_location_id, self.location_data_mapping, self.truck_and_commodity_data, average_fuel_price, path_data)
            price = estimator.estimate()
            return {'list' : [{ 'is_price_estimated': bool(price), 'base_price': price['base_rate'],'distance':price['distance'],'currency':price['currency'], 'truck_type': self.truck_and_commodity_data['truck_name']}]}

    def get_path_from_valhala(self):
        origin_location_id  = self.origin_location_id
        destination_location_id = self.destination_location_id
        path_data = get_path_data(origin_location_id,destination_location_id,self.location_data_mapping)
        return path_data


    def get_average_fuel_price(self,from_valhala,path_data,fuel_type,currency):
        location_ids = []
        location_types = ["city", "district", "region","pincode"]
        if from_valhala:
            for data in path_data:
                location_ids.append(data['id'])
                for location_type in location_types:
                    if data[f"{location_type}_id"]:
                        location_ids.append(data[f"{location_type}_id"])
        else:
            location_ids = path_data

        location_ids = list(set(location_ids))
        all_fuel_price = FuelData.select(FuelData.fuel_price, FuelData.fuel_unit).where(
            FuelData.location_id << location_ids,
            FuelData.location_type << location_types,
            FuelData.fuel_type == fuel_type,
            FuelData.currency == currency,
        )
        all_fuel_price = list(all_fuel_price.dicts())
        avg_fuel_price = 0.0
        for fuel_price_data in all_fuel_price:
            avg_fuel_price += float(fuel_price_data['fuel_price'])

        return avg_fuel_price / len(all_fuel_price)


    def get_country_code(self):
        origin_country_code = self.location_data_mapping[self.origin_location_id]['country_code']
        destination_country_code = self.location_data_mapping[self.destination_location_id]['country_code']
        if origin_country_code == 'IN' and destination_country_code == 'IN':
            return 'IN'
        return 'not_found'
