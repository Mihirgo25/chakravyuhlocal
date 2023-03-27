import requests
import json


def list_location_clusters(params):
    url = "https://api.cogoport.com/location/get_location_cluster"
    response = requests.get(url, json.dumps(params))
    try:
        response = response.content
        return json.loads(response)
    except:
        return {}

def list_locations(params):
    url = "https://api.cogoport.com/location/list_locations"
    response = requests.get(url, {"filters": json.dumps(params), "includes": json.dumps({"continent_id": 1, "trade_id": 1, "country_id": 1, "seaport_id": 1, "default_params_required": 1})})
    try:
        response = response.content
        return json.loads(response)
    except:
        return {}

