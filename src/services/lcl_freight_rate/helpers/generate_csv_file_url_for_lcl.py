from libs.csv_link_generator import get_csv_url
from playhouse.postgres_ext import ServerSide
from playhouse.shortcuts import model_to_dict


def generate_csv_file_url_for_lcl(query):
    csv_urls = []
    rate_count = 0
    final_data = []

    for rate in ServerSide(query):
        if rate_count > 5000:
            rate_count = 0
            csv_url = get_csv_url("lcl_freight", final_data)
            csv_urls.append(csv_url)
            final_data = []

        rate_data = model_to_dict(rate)
        required_coverage_data = get_lcl_freight_coverage_required_data(rate_data)
        final_data.append(required_coverage_data)
        rate_count += 1

    if final_data:
        csv_url = get_csv_url("lcl_freight", final_data)
        csv_urls.append(csv_url)

    return {"urls": csv_urls}


def get_lcl_freight_coverage_required_data(coverage_data):
    required_data = {}
    # required fields to be added when migration is done
    return required_data
