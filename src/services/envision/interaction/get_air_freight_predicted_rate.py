from libs.get_distance import get_air_distance
from configs.definitions import ROOT_DIR
import os, pandas as pd
import joblib, pickle
from configs.ftl_freight_rate_constants import *
from micro_services.client import maps
from datetime import datetime
from configs.definitions import AIR_PREDICTION_MODEL

def predict_air_freight_rate(request):
    if type(request) == dict:
        result = request
    else:
        result = request.__dict__

    airline_path = os.path.join(ROOT_DIR, "services", "envision", "prediction_based_models")
    airline_ranks = pickle.load(open(os.path.join(airline_path,"airline_ranks.pkl"), 'rb'))

    rank = airline_ranks.get(result['airline_id'])
    if not rank:
        rank = 1

    input = {"filters":{"id":[result['origin_airport_id'], result['destination_airport_id']]}}
    data = maps.list_locations(input)
    if data:
        data = data["list"]
    for d in data:
        if d["id"] == result['origin_airport_id']:
            origin_location = (d["latitude"], d["longitude"])
        if d["id"] == result['destination_airport_id']:
            destination_location = (d["latitude"], d["longitude"])
    try:
        Distance = get_air_distance(origin_location[0],origin_location[1], destination_location[0], destination_location[1])
    except:
        Distance = 250

    input_params = [{
        'airline_ranks':rank,
        'air_distance':Distance,
        'commodity':result['commodity'],
        'shipment_type':result['shipment_type'],
        'stacking_type':result['stacking_type'],
        'day_name':datetime.now().strftime('%A'),
        'volume':result['volume']
    }]

    input_df = pd.DataFrame(input_params)
    model_result = AIR_PREDICTION_MODEL.predict(input_df)
    result["predicted_price"] = round(model_result[0], 2)
    return result