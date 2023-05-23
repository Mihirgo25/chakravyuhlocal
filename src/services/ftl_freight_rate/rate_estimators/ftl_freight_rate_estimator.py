from services.ftl_freight_rate.rate_estimators.IN_ftl_freight_rate_estimator import INFtlFreightRateEstimator
from configs.ftl_freight_rate_constants import TRUCK_TYPES_MAPPING,TRUCK_TYPES_MILEAGE_MAPPING
from services.ftl_freight_rate.models.fuel_data import FuelData
import pdb
class FtlFreightEstimator:
    def __init__(self, origin_location_id, destination_location_id,location_data_mapping,truck_and_commodity_data):
        self.origin_location_id = origin_location_id
        self.destination_location_id = destination_location_id
        self.location_data_mapping = location_data_mapping
        self.truck_and_commodity_data = truck_and_commodity_data

    def estimate(self):
        path_data = self.get_path_from_valhala()
        location_data = path_data['location_details']
        country_category  = self.get_country_code()
        if country_category == 'IN':
            pdb.set_trace()
            average_fuel_price = self.get_average_fuel_price(location_data,'diesel','INR')
            estimator = INFtlFreightRateEstimator(self.origin_location_id, self.destination_location_id, self.location_data_mapping, self.truck_and_commodity_data, average_fuel_price, path_data)
            price = estimator.estimate()
            return { 'is_price_estimated': bool(price), 'price': price['base_rate'],'distance':price['distance'],'currency':price['currency'] }
    
    def get_path_from_valhala(self):
        origin_location_id  = self.origin_location_id
        destination_location_id = self.destination_location_id
        return {
        "location_details": [
            {
                "id": "eb187b38-51b2-4a5e-9f3c-978033ca1ddf",
                "pincode_id": "74a228a7-6fcb-4ebd-bd4e-dbd776359f3b",
                "city_id": "4067099b-a672-40e1-b67d-ee58bdb1bbbd",
                "sub_district_id": None,
                "district_id": "161505f5-fbeb-4d6e-87d7-70aae252366f",
                "region_id": None,
                "trade_id": "d1e7b3ca-7518-4706-a644-e99d3aa2e0a9",
                "country_id": None,
            },
            {
                "id": "e7f71802-db3b-4544-9d8f-3da7e1d7f26f",
                "pincode_id": "e309c508-4da0-4516-9038-199ed64d95c9",
                "city_id": "59baa839-29d8-4f4f-9d9b-1eabe9e6729f",
                "sub_district_id": None,
                "district_id": None,
                "region_id": "d25f8326-5d9f-416b-bbe8-81a84e466716",
                "trade_id": "d1e7b3ca-7518-4706-a644-e99d3aa2e0a9",
                "country_id": "541d1232-58ce-4d64-83d6-556a42209eb7",
            },
            {
                "id": "e6eefd7b-17d1-466b-b0c0-ee8cc7999a08",
                "pincode_id": "96c901a5-6403-4106-a8d9-32487489e35d",
                "city_id": "59baa839-29d8-4f4f-9d9b-1eabe9e6729f",
                "sub_district_id": None,
                "district_id": None,
                "region_id": "d25f8326-5d9f-416b-bbe8-81a84e466716",
                "trade_id": "d1e7b3ca-7518-4706-a644-e99d3aa2e0a9",
                "country_id": "541d1232-58ce-4d64-83d6-556a42209eb7",
            },
            {
                "id": "e90c4ccd-bc02-4623-a11a-f5c2980af201",
                "pincode_id": None,
                "city_id": "48a489eb-76d3-419a-bffc-dac6715056d3",
                "sub_district_id": None,
                "district_id": None,
                "region_id": None,
                "trade_id": None,
                "country_id": None,
            },
        ],
        "distance": 162.419,
        "time": 7782.229,
        "distance_units": "kilometers",
        "time_units": "time",
    }

    def get_average_fuel_price(self,path_data,fuel_type,currency):
        return 93.15
        location_ids = []
        location_types = ["city", "district", "region","pincode"]
        for data in path_data:
            location_ids.append(data['id'])
            for location_type in location_types:
                if data[f"{location_type}_id"]:
                    location_ids.append(data[f"{location_type}_id"])
        pdb.set_trace()
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