from libs.additional_service import get_distance
from configs.definitions import ROOT_DIR
import os
import joblib
from micro_services.client import maps
from configs.haulage_freight_rate_constants import weight_limit_constants


def predict_haulage_freight_rate(request):
    if type(request) == dict:
        result = request
    else:
        result = request.__dict__
    origin_location_id = result['origin_location_id']
    destination_location_id = result['destination_location_id']
    container_size = result['container_size'][:2]
    if 'upper_limit' in list(result.keys()):
        if result['upper_limit'] is None or result['upper_limit'] == 0:
            upper_limit = 10
        else:
            upper_limit = result['upper_limit']
    else:
        upper_limit = 10
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
    fuel_used = fuel_consumption(distance,upper_limit)

    MODEL_PATH = os.path.join(ROOT_DIR, "services", "envision", "prediction_based_models", "haulage_freight_prediction_model.pkl")
    model = joblib.load(open(MODEL_PATH, "rb"))
    data = [container_size, upper_limit, distance, fuel_used]
    model_result = model.predict([data])
    result["predicted_price"] = round(model_result[0])
    result["upper_limit"] = upper_limit
    transit_time = (distance//250) * 24
    if transit_time == 0:
        transit_time = 12
    result["transit_time"] = transit_time

    return result

def fuel_consumption(distance,upper_limit):
    if distance < 500:
        if upper_limit < 17:
            litre_per_km = weight_limit_constants['upto_500km']['upto_17_ton']
            fuel_used = distance * litre_per_km
        elif upper_limit < 23:
            litre_per_km = weight_limit_constants['upto_500km']['upto_23_ton']
            fuel_used = distance * litre_per_km
        else:
            litre_per_km = weight_limit_constants['upto_500km']['upto_28_ton']
            fuel_used = distance * litre_per_km
    elif distance < 1000:
        if upper_limit < 17:
            litre_per_km = weight_limit_constants['upto_1000km']['upto_17_ton']
            fuel_used = distance * litre_per_km
        elif upper_limit < 23:
            litre_per_km = weight_limit_constants['upto_1000km']['upto_23_ton']
            fuel_used = distance * litre_per_km
        else:
            litre_per_km = weight_limit_constants['upto_1000km']['upto_28_ton']
            fuel_used = distance * litre_per_km
    else:
        if upper_limit < 17:
            litre_per_km = weight_limit_constants['more_than_1000km']['upto_17_ton']
            fuel_used = distance * litre_per_km
        elif upper_limit < 23:
            litre_per_km = weight_limit_constants['more_than_1000km']['upto_23_ton']
            fuel_used = distance * litre_per_km
        else:
            litre_per_km = weight_limit_constants['more_than_1000km']['upto_28_ton']
            fuel_used = distance * litre_per_km

    return fuel_used