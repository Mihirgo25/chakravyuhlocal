from libs.csv_link_generator import get_csv_url
BATCH_SIZE = 2000

def generate_csv_file_url_for_air(query):

    csv_urls = []
    offset = 0
    while True:
        batch = query.offset(offset).limit(BATCH_SIZE)
        if not batch:
            break
        data = list(query.dicts())
        required_coverage_data = get_air_freight_coverage_required_data(data)                                
        csv_url =  get_csv_url('air_freight', required_coverage_data)
        csv_urls.append(csv_url)
        offset += BATCH_SIZE
    
    return {'urls': csv_urls}

def get_air_freight_coverage_required_data(air_coverage_data):
    list_of_air_coverage_data = []
    for coverage_data in air_coverage_data:
        required_data = {}
        required_data['origin_airport'] = coverage_data['origin_airport']['name']
        required_data['destination_airport'] = coverage_data['destination_airport']['name']
        required_data['origin_airport_code'] = coverage_data['origin_airport']['port_code']
        required_data['destination_port_code'] = coverage_data['destination_airport']['port_code']
        required_data['commodity'] = coverage_data['commodity']
        required_data['airline'] = coverage_data['airline']['short_name'] if coverage_data.get('airline') else None
        required_data['service_provider'] = coverage_data['service_provider']['short_name'] if coverage_data.get('service_provider') else None
        list_of_air_coverage_data.append(required_data)
    return list_of_air_coverage_data

