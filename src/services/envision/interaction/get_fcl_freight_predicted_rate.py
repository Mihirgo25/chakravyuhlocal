from configs.definitions import ROOT_DIR
from configs.fcl_freight_rate_constants import SHIPPING_LINES_FOR_PREDICTION, DEFAULT_WEIGHT_LIMITS_FOR_PREDICTION, DEFAULT_SERVICE_PROVIDER_ID
from configs.global_constants import HAZ_CLASSES
import pickle, joblib, os
from datetime import datetime, timedelta
import pandas as pd, numpy as np, concurrent.futures
from micro_services.client import maps
from configs.env import DEFAULT_USER_ID
from libs.get_distance import get_distance
from services.chakravyuh.interaction.get_shipping_lines_for_prediction import get_shipping_lines_for_prediction
    
def insert_rates_to_rms(create_params):
    from services.fcl_freight_rate.interaction.create_fcl_freight_rate import create_fcl_freight_rate_data    

    for create_param in create_params:
        final_bas_price_to_rms = create_param['line_items'][0]['price']
        create_param['line_items'][0]['price'] = final_bas_price_to_rms + (5 - final_bas_price_to_rms%10) if final_bas_price_to_rms%10 <= 5 else (final_bas_price_to_rms + (10 - final_bas_price_to_rms%10))
        rate_card_id = create_fcl_freight_rate_data(create_param)['id'] 
        create_param['creation_id'] = rate_card_id
        create_param['predicted_price'] = final_bas_price_to_rms

    return create_params

def relevant_shipping_lines(request):
    origin_location_ids = [request['origin_port_id'], request['origin_country_id']]
    destination_location_ids = [request['destination_port_id'], request['destination_country_id']]
    container_size = request['container_size']
    container_type = request['container_type']
    sl_ids = get_shipping_lines_for_prediction(origin_location_ids, destination_location_ids, container_size, container_type)

    if len(sl_ids):
        return sl_ids
    return SHIPPING_LINES_FOR_PREDICTION


def get_fcl_freight_predicted_rate(request):
    from celery_worker import create_fcl_freight_rate_feedback_for_prediction
    if type(request) == dict:
        request = request
    else:
        request = request.__dict__
    
    location_data = maps.list_locations_mapping({'location_id':[request['origin_port_id'],request['destination_port_id']],'type':['main_ports']})
    if location_data and isinstance(location_data, dict):
        location_data = location_data['list']
    else:
        location_data = []

    origin_main_port_ids = []
    destination_main_port_ids = []

    for loc in location_data:
        if loc['icd_port_id'] == request['origin_port_id']:
            origin_main_port_ids.append(loc['id'])
        elif loc['icd_port_id'] == request['destination_port_id']:
            destination_main_port_ids.append(loc['id'])

    if len(origin_main_port_ids) == 0:
        origin_main_port_ids.append(request['origin_port_id'])
    elif len(origin_main_port_ids) > 2:
        origin_main_port_ids = origin_main_port_ids[:2]
        
    if len(destination_main_port_ids) == 0:
        destination_main_port_ids.append(request['destination_port_id'])
    elif len(destination_main_port_ids) > 2:
        destination_main_port_ids = destination_main_port_ids[:2]

    all_shipping_lines = relevant_shipping_lines(request)
    if request.get('shipping_line_id'):
        all_shipping_lines = [request.get('shipping_line_id')]

    data_for_feedback = []
    for origin_port_id in origin_main_port_ids:
        for destination_port_id in destination_main_port_ids:
            ports_distance = maps.get_sea_route({'origin_port_id':origin_port_id, 'destination_port_id':destination_port_id, 'includes':['length']})
            if ports_distance and isinstance(ports_distance, dict):
                ports_distance = ports_distance['length']['length']
            else:
                port_dict = joblib.load(open(os.path.join(ROOT_DIR, "services", "envision", "prediction_based_models", "seaports_dict.pkl") , "rb"))
                ports_distance = get_distance(port_dict.get(request['origin_port_id']), port_dict.get(request['destination_port_id']))
            with concurrent.futures.ThreadPoolExecutor(max_workers = len(all_shipping_lines)) as executor:
                futures = [executor.submit(predict_rates, origin_port_id, destination_port_id, shipping_line_id, request, ports_distance) for shipping_line_id in all_shipping_lines]
            data_for_feedback.extend(futures)

    for i in range(len(data_for_feedback)):
        data_for_feedback[i] = data_for_feedback[i].result()
    

    if request.get('is_source_lcl'):
        return data_for_feedback
    
    data_for_feedback = insert_rates_to_rms(data_for_feedback)

    create_fcl_freight_rate_feedback_for_prediction.apply_async(kwargs={'result':data_for_feedback}, queue = 'low')

def predict_rates(origin_port_id, destination_port_id, shipping_line_id, request, ports_distance):
    validity_start = datetime.now().date().isoformat()
    validity_end = (datetime.now() + timedelta(days = 7)).date().isoformat()

    MODEL_PATH = os.path.join(ROOT_DIR, "services", "envision", "prediction_based_models", "fcl_freight_forecasting_model.pkl")
    shipping_line_dict = pickle.load(open(os.path.join(ROOT_DIR, "services", "envision", "prediction_based_models","shipping_line.pkl"), 'rb'))
    model = joblib.load(open(MODEL_PATH, "rb"))

    if request['origin_country_id'] == request['destination_country_id']:
        countries_distance = 1
    else:
        countries_distance = ports_distance

    df = pd.DataFrame()
    df['container_size'] = [int(request['container_size'][:2])]
    if shipping_line_dict.get(shipping_line_id):
        df['shipping_line_rank'] = [shipping_line_dict[shipping_line_id]]
    else:
        df['shipping_line_rank'] = [1]
    df['Distance'] = [ports_distance]
    df['Country_Distance'] = [countries_distance]
    df['ds'] = validity_start

    model_request = model.predict(df)['yhat']
    price =  round(np.exp(model_request[0]))

    creation_param = {
        'origin_port_id': request['origin_port_id'],
        'destination_port_id': request['destination_port_id'],
        'origin_country_id':request['origin_country_id'],
        'destination_country_id':request['destination_country_id'],
        'container_size': request['container_size'],
        'container_type': request['container_type'],
        'commodity': request['commodity'] if request.get('commodity') else 'general',
        'shipping_line_id' : shipping_line_id,
        'service_provider_id' : DEFAULT_SERVICE_PROVIDER_ID,
        'validity_start': datetime.strptime(validity_start,'%Y-%m-%d'),
        'validity_end': datetime.strptime(validity_end,'%Y-%m-%d'),
        'line_items': [
        {
            "code": "BAS",
            "unit": "per_container",
            "price" : price,
            "currency": "USD",
            "remarks": [],
            "slabs": []
        }
        ],
        'weight_limit': DEFAULT_WEIGHT_LIMITS_FOR_PREDICTION[request['container_size']],
        'origin_local': {
                'plugin': None,
                'line_items': []
        },
        'destination_local':
        {
                'plugin': None,
                'line_items': []
        },
        'performed_by_id': DEFAULT_USER_ID,
        'procured_by_id': DEFAULT_USER_ID,
        'sourced_by_id': DEFAULT_USER_ID,
        'source':'predicted_rate',
        'mode':'predicted',
        'accuracy':60
    }
    if request['container_type'] in ['open_top', 'flat_rack', 'iso_tank'] or request['container_size'] == '45HC':
        creation_param['line_items'].append({
            "code": "SPE",
            "unit": "per_container",
            "price": 0,
            "currency": "USD",
            "remarks": [
            ],
            "slabs": []
        })
    
    if request['commodity'] in HAZ_CLASSES:
        creation_param['line_items'].append({
            "code": "HSC",
            "unit": "per_container",
            "price": 0,
            "currency": "USD",
            "remarks": [
            ],
            "slabs": []
        })

    if origin_port_id != request['origin_port_id']:
        creation_param['origin_main_port_id'] = origin_port_id
    
    if destination_port_id != request['destination_port_id']:
        creation_param['destination_main_port_id'] = destination_port_id

    if creation_param['destination_country_id'] == '541d1232-58ce-4d64-83d6-556a42209eb7':
        creation_param['line_items'][0]['price'] = creation_param['line_items'][0]['price'] + 100

    return creation_param
    