from scheduler import scheduler
from schedule import every
import json
from micro_services.client import *
from services.ftl_freight_rate.models.fuel_data import FuelData

@scheduler.add(every(4).days)
def scheduler_trending():
    print('yes')
    fuel_data = scrap_data_for_india()['data']
    
    location_names = list(set((map(lambda data:data['location_name'],fuel_data))))
    location_types = list(set(map(lambda data:data['location_type'],fuel_data)))
    input = {"filters":json.dumps({"name":location_names,"type":location_types})}
    location_data = maps.list_locations(input)["list"]
    fuel_data_mapping = get_fuel_data_mapping(fuel_data, location_data)
    for fuel_data in fuel_data_mapping:
        q = FuelData.get_or_create(**fuel_data)

def get_fuel_data_mapping(fuel_data_list, locations):
    data = []
    for fuel_data in fuel_data_list:
        location_data = list(filter(lambda data:data['name'] == fuel_data['location_name'],locations))
        if location_data:
            fuel_data['location_id'] = location_data[0]['id']
        final_data = {}
        for key, values in fuel_data.items():
            if key not in ['id', 'location_name']:
                final_data[key] = values
        data.append(final_data)
    
    return data

def scrap_data_for_india():
    return {
        "data": [
            {
                "id":1,
                "location_name": "Maharashtra",
                "fuel_type": "petrol",
                "fuel_price": 105.96,
                "currency": "INR",
                "fuel_unit": "litre",
                "location_type":'region'
            },
            {
                "id":2,
                "location_name": "Hyderabad",
                "fuel_type": "petrol",
                "fuel_price": 109.66,
                "currency": "INR",
                "fuel_unit": "litre",
                "location_type":'city'
            },
            {
                "id":3,
                "location_name": "Uttar Pradesh",
                "fuel_type": "petrol",
                "fuel_price": 96.38,
                "currency": "INR",
                "fuel_unit": "litre",
                "location_type":'region'
            },
            {
                "id":4,
                "location_name": "Andhra Pradesh",
                "fuel_type": "petrol",
                "fuel_price": 110.48,
                "currency": "INR",
                "fuel_unit": "litre",
                "location_type":'region',
            },
            {
                "id":5,
                "location_name": "Assam",
                "fuel_type": "petrol",
                "fuel_price": 97.16,
                "currency": "INR",
                "fuel_unit": "litre",
                "location_type":'region'
            },
            {
                "id":6,
                "location_name": "Chandigarh",
                "fuel_type": "petrol",
                "fuel_price": 96.2,
                "currency": "INR",
                "fuel_unit": "litre",
                "location_type":'region'
            },
            {
                "id":7,
                "location_name": "Karnataka",
                "fuel_type": "petrol",
                "fuel_price": 101.94,
                "currency": "INR",
                "fuel_unit": "litre",
                "location_type":"region"
            },
            {
                "id":8,
                "location_name": "Madhya Pradesh",
                "fuel_type": "petrol",
                "fuel_price": 108.65,
                "currency": "INR",
                "fuel_unit": "litre",
                "location_type":"region"
            },
        ]
    }