from scheduler import scheduler
from schedule import every
# from schedule import every
from micro_services.client import *
from services.ftl_freight_rate.models.fuel_data import FuelData

@scheduler.add(every(1).second, name="trending_redis")
def scheduler_trending():
    print('yes')
    # fuel_data = scrap_data_for_india()['data']
    # location_names = map(lambda data:data['location_name'],fuel_data)
    # location_types = map(lambda data:data['location_types'],fuel_data)
    # location_ids = maps.list_locations({"filters": {"name": location_names, "type": location_types}})["list"]


# def scrap_data_for_india():
#     return {
#         "data": [
#             {
#                 "location_name": "Maharashtra",
#                 "fuel_type": "petrol",
#                 "fuel_price": "105.96",
#                 "currency": "INR",
#                 "fuel_unit": "litre",
#             },
#             {
#                 "location_name": "Hyderabad",
#                 "fuel_type": "petrol",
#                 "fuel_price": "109.66",
#                 "currency": "INR",
#                 "fuel_unit": "litre",
#             },
#             {
#                 "location_name": "Uttar Pradesh",
#                 "fuel_type": "petrol",
#                 "fuel_price": "96.38",
#                 "currency": "INR",
#                 "fuel_unit": "litre",
#             },
#             {
#                 "location_name": "Andhra Pradesh",
#                 "fuel_type": "petrol",
#                 "fuel_price": "110.48",
#                 "currency": "INR",
#                 "fuel_unit": "litre",
#             },
#             {
#                 "location_name": "Assam",
#                 "fuel_type": "petrol",
#                 "fuel_price": "97.16",
#                 "currency": "INR",
#                 "fuel_unit": "litre",
#             },
#             {
#                 "location_name": "Chandigarh",
#                 "fuel_type": "petrol",
#                 "fuel_price": "96.2",
#                 "currency": "INR",
#                 "fuel_unit": "litre",
#             },
#             {
#                 "location_name": "Karnataka",
#                 "fuel_type": "petrol",
#                 "fuel_price": "101.94",
#                 "currency": "INR",
#                 "fuel_unit": "litre",
#             },
#             {
#                 "location_name": "Madhya Pradesh",
#                 "fuel_type": "petrol",
#                 "fuel_price": "108.65",
#                 "currency": "INR",
#                 "fuel_unit": "litre",
#             },
#         ]
#     }
