from libs.csv_link_generator import get_csv_url

def generate_csv_file_url_for_haulage(query):
    data = list(query.dicts())
    required_coverage_data = get_haulage_freight_coverage_required_data(data)                                
    csv_url =  get_csv_url('haulage_freight', required_coverage_data)
    return {'url': csv_url}


def get_haulage_freight_coverage_required_data(haulage_coverage_data):
    list_of_haulage_coverage_data = []
    for coverage_data in haulage_coverage_data:
        required_data = {}
        required_data['origin_location'] = coverage_data['origin_location']['name']
        required_data['destination_location'] = coverage_data['destination_location']['name']
        required_data['origin_location_id'] = coverage_data['origin_location_id']['port_code']
        required_data['destination_location_id'] = coverage_data['destination_location_id']['port_code']
        required_data['commodity'] = coverage_data['commodity']
        required_data['container_type']  = coverage_data['container_type']
        required_data['container_size'] = coverage_data['container_size']
        required_data['shipping_line'] = coverage_data['shipping_line']['short_name'] if coverage_data.get('shipping_line') else None
        required_data['service_provider'] = coverage_data['service_provider']['short_name'] if coverage_data.get('service_provider') else None
        list_of_haulage_coverage_data.append(required_data)
    return list_of_haulage_coverage_data