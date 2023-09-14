from libs.csv_link_generator import get_csv_url
from playhouse.postgres_ext import ServerSide
from playhouse.shortcuts import model_to_dict


def generate_csv_file_url_for_fcl(query):
    csv_urls = []
    final_data = []

    for rate in ServerSide(query):
        if len(final_data) > 5000:
            csv_url = get_csv_url("fcl_freight", final_data)
            csv_urls.append(csv_url)
            final_data = []

        rate_data = model_to_dict(rate)
        required_coverage_data = get_fcl_freight_coverage_required_data(rate_data)
        final_data.append(required_coverage_data)

    if final_data:
        csv_url = get_csv_url("fcl_freight", final_data)
        csv_urls.append(csv_url)

    return {"urls": csv_urls}
                         
        

def get_fcl_freight_coverage_required_data(coverage_data):
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
    return required_data
