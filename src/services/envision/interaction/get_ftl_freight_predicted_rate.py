from libs.get_distance import get_distance
from configs.definitions import ROOT_DIR
import os
import joblib
from configs.ftl_freight_rate_constants import *
from micro_services.client import maps


def predict_ftl_freight_rate(request):
    if type(request) == dict:
        result = request
    else:
        result = request.__dict__
    origin_location_id = result.get('origin_location_id')
    destination_location_id = result['destination_location_id']
    origin_region_id = result['origin_region_id'] if result['origin_region_id'] is not None else DEFAULT_REGION_ID_PREDICTION
    destination_region_id = result['destination_region_id'] if result['destination_region_id'] is not None else DEFAULT_REGION_ID_PREDICTION
    truck_type = result['truck_type']
    tyre = PREDICTION_TRUCK_TYPES[truck_type]['tyre']
    weight = PREDICTION_TRUCK_TYPES[truck_type]['weight']
    volume = PREDICTION_TRUCK_TYPES[truck_type]['volume']
    ltr_per_km = 1/PREDICTION_TRUCK_TYPES[truck_type]['mileage']
    origin_gdp = REGION_ID_GDP[origin_region_id]
    destination_gdp = REGION_ID_GDP[destination_region_id]
    input = {"filters":{"id":[origin_location_id, destination_location_id]}}
    data = maps.list_locations(input)
    if data:
        data = data["list"]
    for d in data:
        if d["id"] == origin_location_id:
            origin_location = (d["latitude"], d["longitude"])
        if d["id"] == destination_location_id:
            destination_location = (d["latitude"], d["longitude"])
    try:
        distance = get_distance(origin_location,destination_location)
    except:
        distance = 250
    MODEL_PATH = os.path.join(ROOT_DIR, "services", "envision", "prediction_based_models", "ftl_freight_prediction_model.pkl")
    model = joblib.load(open(MODEL_PATH, "rb"))
    data = [tyre, weight, volume, ltr_per_km, distance, origin_gdp, destination_gdp]
    model_result = model.predict([data])
    result["predicted_price"] = round(model_result[0])
    result["distance"] = distance

    return result
