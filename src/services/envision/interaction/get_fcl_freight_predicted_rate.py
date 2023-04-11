from configs.definitions import ROOT_DIR
from configs.fcl_freight_rate_constants import SHIPPING_LINES_FOR_PREDICTION, DEFAULT_WEIGHT_LIMITS_FOR_PREDICTION, DEFAULT_SERVICE_PROVIDER_ID
from configs.global_constants import HAZ_CLASSES
import pickle, joblib, os
from datetime import datetime, timedelta
import pandas as pd, numpy as np, concurrent.futures
from micro_services.client import maps
from configs.env import DEFAULT_USER_ID

def get_fcl_freight_predicted_rate(request):
    from celery_worker import create_fcl_freight_rate_feedback_for_prediction
    if type(request) == dict:
        request = request
    else:
        request = request.__dict__

    location_data = maps.list_locations_mapping({'location_id':[request['origin_port_id'],request['destination_port_id']],'type':['main_ports']})['list']

    origin_main_port_ids = []
    destination_main_port_ids = []

    for loc in location_data:
        if loc['country_id'] == request['origin_country_id']:
            origin_main_port_ids.append(loc['id'])
        elif loc['country_id'] == request['destination_country_id']:
            destination_main_port_ids.append(loc['id'])

    if len(origin_main_port_ids) == 0:
        origin_main_port_ids.append(request['origin_port_id'])
    elif len(origin_main_port_ids) > 2:
        origin_main_port_ids = origin_main_port_ids[:2]
        
    if len(destination_main_port_ids) == 0:
        destination_main_port_ids.append(request['destination_port_id'])
    elif len(destination_main_port_ids) > 2:
        destination_main_port_ids = destination_main_port_ids[:2]

    all_shipping_lines = SHIPPING_LINES_FOR_PREDICTION
    if request.get('shipping_line_id'):
        all_shipping_lines = [request.get('shipping_line_id')]

    data_for_feedback = []
    for origin_port_id in origin_main_port_ids:
        for destination_port_id in destination_main_port_ids:
            ports_distance = maps.get_sea_route({'origin_port_id':origin_port_id, 'destination_port_id':destination_port_id})
            if ports_distance:
                ports_distance = ports_distance['length']['length']
            with concurrent.futures.ThreadPoolExecutor(max_workers = len(all_shipping_lines)) as executor:
                futures = [executor.submit(predict_rates, origin_port_id, destination_port_id, shipping_line_id, request, ports_distance) for shipping_line_id in all_shipping_lines]
            data_for_feedback.extend(futures)

    for i in range(len(data_for_feedback)):
        data_for_feedback[i] = data_for_feedback[i].result()

    if request.get('is_source_lcl'):
        return data_for_feedback

    create_fcl_freight_rate_feedback_for_prediction.apply_async(kwargs={'result':data_for_feedback}, queue = 'low')

def predict_rates(origin_port_id, destination_port_id, shipping_line_id, request, ports_distance):
    from services.fcl_freight_rate.interaction.create_fcl_freight_rate import create_fcl_freight_rate_data
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
    df['shipping_line_rank'] = [shipping_line_dict[shipping_line_id]] 
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
            "price" : price + (5 - price%10) if price%10 <= 5 else (price + (10 - price%10)),
            "currency": "USD",
            "remarks": []            ,
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

    if request.get('is_source_lcl'):
        return creation_param

    rate_card_id = create_fcl_freight_rate_data(creation_param)['id'] 
    creation_param['creation_id'] = rate_card_id
    return creation_param