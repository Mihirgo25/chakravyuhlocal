from services.envision.helpers.csv_link_generator import get_csv_url
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_coverages import list_fcl_freight_rate_coverages
from services.air_freight_rate.interactions.list_air_freight_rate_coverages import list_air_freight_rate_coverages
import copy
import json
def generate_csv_file_url(filters):
    if filters:
        if type(filters) != dict:
           filters = json.loads(filters)
    
    service_type = filters.get('service')
    required_coverage_data = []
    if service_type == 'fcl_freight':
        fcl_coverage_data = list_fcl_freight_rate_coverages(filters = filters,generate_csv_url = True)['list']
        required_coverage_data =  get_fcl_coverage_required_data(fcl_coverage_data)
    else:
        air_coverage_data = list_air_freight_rate_coverages(filters = filters, generate_csv_url = True)['list']   
        required_coverage_data = get_air_coverage_required_data(air_coverage_data)
    
    csv_url =  get_csv_url(service_type, required_coverage_data)
    
    return {'url': csv_url}
    

def get_fcl_coverage_required_data(fcl_coverage_data):
    list_of_fcl_coverage_data = []
    for coverage_data in fcl_coverage_data:
        required_data = {}
        required_data['origin_port'] = coverage_data['origin_port']['name']
        required_data['destination_port'] = coverage_data['destination_port']['name']
        required_data['commodity'] = coverage_data['commodity']
        required_data['container_type']  = coverage_data['container_type']
        required_data['container_size'] = coverage_data['container_size']
        required_data['shipping_line'] = coverage_data['shipping_line']['short_name'] if coverage_data.get('shipping_line') else None
        required_data['service_provider'] = coverage_data['service_provider']['short_name'] if coverage_data.get('service_provider') else None
        list_of_fcl_coverage_data.append(copy.deepcopy(required_data))
    return list_of_fcl_coverage_data

def get_air_coverage_required_data(air_coverage_data):
    list_of_air_coverage_data = []
    for coverage_data in air_coverage_data:
        required_data = {}
        required_data['origin_airport'] = coverage_data['origin_airport']['name']
        required_data['destination_airport'] = coverage_data['destination_airport']['name']
        required_data['commodity'] = coverage_data['commodity']
        required_data['airline'] = coverage_data['airline']['short_name'] if coverage_data.get('airline') else None
        required_data['service_provider'] = coverage_data['service_provider']['short_name'] if coverage_data.get('service_provider') else None
        list_of_air_coverage_data.append(copy.deepcopy(required_data))
    return list_of_air_coverage_data

