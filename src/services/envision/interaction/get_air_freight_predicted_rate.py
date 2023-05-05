from libs.additional_service import get_distance
from configs.definitions import ROOT_DIR
import os
import joblib, pickle
from configs.ftl_freight_rate_constants import *
from micro_services.client import maps

def predict_air_freight_rate(request):
    if type(request) == dict:
        result = request
    else:
        result = request.__dict__ 
    weight = result['weight']
    packages_count = result['packages_count']
    volume = result['volume']
    airline_id = result['airline_id']
    origin_airport_id = result['origin_airport_id']
    destination_airport_id = result['destination_airport_id']
    date = result['date']

    airline_path = os.path.join(ROOT_DIR, "services", "envision", "prediction_based_models")
    airline_ranks = pickle.load(open(os.path.join(airline_path,"airline_ranks.pkl"), 'rb'))   
    
    ranks = airline_ranks[airline_id]

    input = {"filters":{"id":[origin_airport_id, destination_airport_id]}}
    data = maps.list_locations(input)
    if data:
        data = data["list"]
    for d in data:
        if d["id"] == origin_airport_id:
            origin_location = (d["latitude"], d["longitude"])
        if d["id"] == destination_airport_id:
            destination_location = (d["latitude"], d["longitude"])
    try:
        Distance = get_distance(origin_location,destination_location)
    except:
        Distance = 250

    
    MODEL_PATH = os.path.join(ROOT_DIR, "projects", "cogo_envision", "pred_model", "air_freight_prediction_model.pkl")
    model = pickle.load(open(MODEL_PATH, 'rb'))
    data = [weight, packages_count, volume, ranks, Distance]
    model_result = model.predict([data])
    result["predicted_price"] = round(model_result[0])

    return result