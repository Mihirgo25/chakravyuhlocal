from libs.csv_link_generator import get_csv_url
BATCH_SIZE = 5000 

def generate_csv_file_url_for_fcl(query):
    csv_urls = []
    offset = 0
    while True:
        batch = query.offset(offset).limit(BATCH_SIZE)
        if not batch:
            break
        data = list(query.dicts())
        required_coverage_data = get_fcl_freight_coverage_required_data(data) 
        csv_url =  get_csv_url('fcl_freight', required_coverage_data) 
        csv_urls.append(csv_url)
        offset += BATCH_SIZE
                         
    return {'urls': csv_urls}
        

def get_fcl_freight_coverage_required_data(fcl_coverage_data):
    list_of_fcl_coverage_data = []
    for coverage_data in fcl_coverage_data:
        required_data = {}
        required_data['origin_port'] = coverage_data['origin_port']['name']
        required_data['destination_port'] = coverage_data['destination_port']['name']
        required_data['origin_port_code'] = coverage_data['origin_port']['port_code']
        required_data['destination_port_code'] = coverage_data['destination_port']['port_code']
        required_data['commodity'] = coverage_data['commodity']
        required_data['container_type']  = coverage_data['container_type']
        required_data['container_size'] = coverage_data['container_size']
        required_data['shipping_line'] = coverage_data['shipping_line']['short_name'] if coverage_data.get('shipping_line') else None
        required_data['service_provider'] = coverage_data['service_provider']['short_name'] if coverage_data.get('service_provider') else None
        list_of_fcl_coverage_data.append(required_data)
    return list_of_fcl_coverage_data
