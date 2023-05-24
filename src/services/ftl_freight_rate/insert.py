import pandas as pd
from services.ftl_freight_rate.models.truck import Truck

path_to_csv = '/Users/rasswanth/Desktop/data/india-mileage-added.csv'

def insert():
    df = pd.read_csv(path_to_csv,index_col=0)

    for index, row in df.iterrows():

        row_data = {
            'truck_company' : row['truck_company'],
            'truck_name' : row['truck_name'],
            'display_name' : row['display_name'],
            'vehicle_weight' : row['vehicle_weight'],
            'vehicle_weight_unit' : row['vehicle_weight_unit'],
            'fuel_type' : row['fuel_type'],
            'no_of_wheels' : row['no_of_wheels'],
            'engine_type' : row['engine_type'],
            'truck_type' : row['truck_type'],
            'body_type' : row['body_type'],
            'mileage' : row['mileage'],
            'mileage_unit' : row['mileage_unit'],
            'status': 'active',
            'country_id' : '541d1232-58ce-4d64-83d6-556a42209eb7'
        }

        Truck.create(**row_data)

    print("inserted")
