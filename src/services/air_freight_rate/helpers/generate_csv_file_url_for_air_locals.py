from libs.csv_link_generator import get_csv_url
from playhouse.postgres_ext import ServerSide
from playhouse.shortcuts import model_to_dict


def generate_csv_file_url_for_air_locals(query):
    csv_urls = []
    rate_count = 0
    final_data = []

    for rate in ServerSide(query):
        if rate_count > 5000:
            rate_count = 0
            csv_url = get_csv_url("air_freight_local", final_data)
            csv_urls.append(csv_url)
            final_data = []

        rate_data = model_to_dict(rate)
        required_coverage_data = get_air_freight_local_coverage_required_data(rate_data)
        final_data.append(required_coverage_data)
        rate_count += 1

    if final_data:
        csv_url = get_csv_url("air_freight_local", final_data)
        csv_urls.append(csv_url)

    return {"urls": csv_urls}


def get_air_freight_local_coverage_required_data(coverage_data):
    required_data = {}
    required_data["airport"] = coverage_data["origin_airport"]["name"]
    required_data["commodity"] = coverage_data["commodity"]
    required_data["commodity_sub_type"] = coverage_data["commodity_sub_type"]
    required_data["trade_type"] = coverage_data["trade_type"]
    required_data["airline"] = (
        coverage_data["airline"]["short_name"] if coverage_data.get("airline") else None
    )
    required_data["service_provider"] = (
        coverage_data["service_provider"]["short_name"]
        if coverage_data.get("service_provider")
        else None
    )
    return required_data
