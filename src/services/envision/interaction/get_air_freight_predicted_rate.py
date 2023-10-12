from configs.definitions import ROOT_DIR
import os, pandas as pd
import pickle
from datetime import datetime
from configs.yml_definitions import AIR_PREDICTION_MODEL

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

    input_params = [{
        'airline_ranks':rank,
        'air_distance':result['air_distance'],
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