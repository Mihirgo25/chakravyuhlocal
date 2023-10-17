from libs.csv_link_generator import get_csv_url
from playhouse.postgres_ext import ServerSide
from playhouse.shortcuts import model_to_dict

def generate_csv_file_url_for_haulage(query):
    csv_urls = []
    rate_count = 0
    final_data = []

    for rate in ServerSide(query):
        if rate_count > 5000:
            rate_count = 0
            csv_url = get_csv_url("haulage_freight", final_data)
            csv_urls.append(csv_url)
            final_data = []


        rate_data = model_to_dict(rate)
        required_coverage_data = get_haulage_freight_coverage_required_data(rate_data)
        final_data.append(required_coverage_data)
        rate_count += 1

    if final_data:
        csv_url = get_csv_url("haulage_freight", final_data)
        csv_urls.append(csv_url)

    return {"urls": csv_urls}


def get_haulage_freight_coverage_required_data(haulage_coverage_data):
    list_of_haulage_coverage_data = []
    for coverage_data in haulage_coverage_data:
        required_data = {}
        required_data['origin_location'] = coverage_data['origin_location']['name']
        required_data['destination_location'] = coverage_data['destination_location']['name']
        required_data['origin_location_id'] = coverage_data['origin_location']['id']
        required_data['destination_location_id'] = coverage_data['destination_location']['id']
        required_data['commodity'] = coverage_data['commodity']
        required_data['container_type']  = coverage_data['container_type']
        required_data['container_size'] = coverage_data['container_size']
        required_data['shipping_line'] = coverage_data['shipping_line']['short_name'] if coverage_data.get('shipping_line') else None
        required_data['service_provider'] = coverage_data['service_provider']['short_name'] if coverage_data.get('service_provider') else None
        list_of_haulage_coverage_data.append(required_data)
    return list_of_haulage_coverage_data