from configs.definitions import ROOT_DIR
from configs.fcl_freight_rate_constants import SHIPPING_LINE_SERVICE_PROVIDER_FOR_PREDICTION
import pickle, joblib, os, geopy.distance
from datetime import datetime, timedelta
from celery_worker import create_fcl_freight_rate_feedback_for_prediction
import pandas as pd
import numpy as np


def port_distance(cord1, cord2):
    coords_1 = cord1
    coords_2 = cord2
    return geopy.distance.geodesic(coords_1, coords_2).km

def get_fcl_freight_predicted_rate(request, key):
    if type(request) == dict:
        request = request
    else:
        request = request.__dict__
    location_dict = joblib.load(open(os.path.join(ROOT_DIR, "utils", "prediction_based_models", "location_distance.pkl"), "rb"))
    MODEL_PATH = os.path.join(ROOT_DIR, "utils", "prediction_based_models", "fcl_freight_forecasting_model.pkl")
    shipping_line_dict = pickle.load(open(os.path.join(ROOT_DIR, "utils", "prediction_based_models","shipping_line.pkl"), 'rb'))
    port_id_country_id_dict = pickle.load(open(os.path.join(ROOT_DIR, "utils", "prediction_based_models", "port_id_country_id.pkl"),'rb'))
    origin_main_port_dict = pickle.load(open(os.path.join(ROOT_DIR, "utils", "prediction_based_models","icd_dict.pkl"), 'rb'))
    destination_main_port_dict = pickle.load(open(os.path.join(ROOT_DIR, "utils", "prediction_based_models","shipping_line.pkl"), "rb"))
    request['origin_country_id'] = port_id_country_id_dict[str(request['origin_port_id'])]
    request['destination_country_id'] = port_id_country_id_dict[str(request['destination_port_id'])]
    ports_distance = port_distance(location_dict[str(request['origin_port_id'])],location_dict[str(request['destination_port_id'])])
    origin_country_id = port_id_country_id_dict[str(request['origin_port_id'])]
    destination_country_id = port_id_country_id_dict[str(request['destination_port_id'])]
    if origin_country_id == destination_country_id:
        countries_distance = 1
    else:
        countries_distance = port_distance(location_dict[origin_country_id],location_dict[destination_country_id])
    container_size = int(request['container_size'][:2])
    model = joblib.load(open(MODEL_PATH, "rb"))
    if key == 'expired_objects':
        validity_start = datetime.now()
        validity_end = datetime.now() + timedelta(days = 14)
        df = pd.DataFrame()
        df['container_size'] = [container_size]
        df['shipping_line_rank'] = shipping_line_dict[str(request['shipping_line_id'])]

        df['Distance'] = [ports_distance]
        df['Country_Distance'] = [countries_distance]
        df['ds'] = validity_start
        model_result = model.predict(df)['yhat']
        request["predicted_price"] = round(np.exp(model_result[0]),1)
        request["validity_start"] = validity_start.date()
        request["validity_end"] = validity_end.date()
        return request
    
    else:
        validity_start = datetime.now().date().isoformat()
        validity_end = (datetime.now() + timedelta(days = 7)).date().isoformat()
        request['origin_main_port_id'] = origin_main_port_dict.get(request['origin_port_id'], None)
        request['destination_main_port_id'] = destination_main_port_dict.get(request['destination_port_id'], None)

        if request['shipping_line_id']:
            SHIPPING_LINE_SERVICE_PROVIDER_FOR_PREDICTION[request['shipping_line_id']] = request['service_provider_id']

        freight_rates = []
        for shipping_line_id in SHIPPING_LINE_SERVICE_PROVIDER_FOR_PREDICTION.keys():
            df = pd.DataFrame()
            df['container_size'] = [container_size]
            df['shipping_line_rank'] = [shipping_line_dict[shipping_line_id]] 
            df['Distance'] = [ports_distance]
            df['Country_Distance'] = [countries_distance]
            df['ds'] = validity_start

            model_request = model.predict(df)['yhat']
            response = {
                'id' : str(datetime.now().timestamp()).replace('.',''),
                'validities' : [{
                    'id' : None,
                    'price':round(np.exp(model_request[0])),
                    'line_items': 
                    [{'code': 'BAS',
                    'unit': 'per_container',
                    'price': round(np.exp(model_request[0])),
                    'slabs': [],
                    'remarks': [],
                    'currency': 'USD'
                    }],
                'likes_count': 0,
                'payment_term': 'prepaid',
                'validity_end': validity_end,
                'schedule_type': 'transhipment',
                'dislikes_count': 0,
                'platform_price': round(np.exp(model_request[0])),
                'validity_start': validity_start
                }],
                'container_size': request['container_size'],
                'container_type': request['container_type'],
                'commodity': request['commodity'],
                'origin_port_id': request['origin_port_id'],
                'destination_port_id': request['destination_port_id'],
                'origin_country_id': request['origin_country_id'],
                'destination_country_id': request['destination_country_id'],
                'origin_main_port_id': request['origin_main_port_id'],
                'destination_main_port_id': request['destination_main_port_id'],
                'importer_exporter_id': request['importer_exporter_id'],
                'shipping_line_id' : shipping_line_id,
                'service_provider_id' : SHIPPING_LINE_SERVICE_PROVIDER_FOR_PREDICTION[shipping_line_id],
                'weight_limit': {
                },
                'origin_local': {
                        'plugin': None,
                        'line_items': []
                    },
                'destination_local': {
                        'plugin': None,
                        'line_items': []
                    },
                'is_origin_local_line_items_error_messages_present': True,
                'is_destination_local_line_items_error_messages_present': True,
                'cogo_entity_id': request['cogo_entity_id']
            }

            freight_rates.append(response)
        create_fcl_freight_rate_feedback_for_prediction.apply_async(kwargs = {'result':freight_rates}, queue = 'low')
        return freight_rates