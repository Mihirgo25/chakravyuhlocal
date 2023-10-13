from libs.csv_link_generator import get_csv_url
from playhouse.postgres_ext import ServerSide
from playhouse.shortcuts import model_to_dict


def generate_csv_file_url_for_ltl(query):
    csv_urls = []
    rate_count = 0
    final_data = []

    for rate in ServerSide(query):
        if rate_count > 5000:
            rate_count = 0
            csv_url = get_csv_url("ltl_freight", final_data)
            csv_urls.append(csv_url)
            final_data = []


        rate_data = model_to_dict(rate)
        required_coverage_data = get_ltl_freight_coverage_required_data(rate_data)
        final_data.append(required_coverage_data)
        rate_count += 1

    if final_data:
        csv_url = get_csv_url("ltl_freight", final_data)
        csv_urls.append(csv_url)

    return {"urls": csv_urls}
                         
        

def get_ltl_freight_coverage_required_data(coverage_data):
    required_data = {}
    breakpoint()
    required_data['origin_location'] = coverage_data['origin_location']['name']
    required_data['origin_port_code'] = coverage_data['origin_location']['port_code']
    required_data['destination_location'] = coverage_data['destination_location']['name']
    required_data['destination_port_code'] = coverage_data['destination_location']['port_code']
    required_data['commodity'] = coverage_data['commodity']
    required_data['density_factor']  = coverage_data['density_factor']
    required_data['transit_time'] = coverage_data['transit_time']
    required_data['trip_type'] = coverage_data['trip_type']
    required_data['service_provider'] = coverage_data['service_provider']['short_name'] if coverage_data.get('service_provider') else None
    return required_data
