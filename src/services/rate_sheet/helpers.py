import os
import httpx
from database.db_session import rd
from datetime import datetime
import dateutil.parser as parser
from libs.parse_numeric import parse_numeric
from database.rails_db import get_operators
from micro_services.client import maps
from database.rails_db import get_operators

client = httpx.Client()


current_processing_line = "last_line"
total_line_hash = "total_line"
error_present_hash = "error_present"
processed_percent_hash = "process_percent"
VALID_LOCATION_TYPES = ["city", "pincode", "railway_terminal", "railway_station"]


def get_original_file_path(params):
    path = os.path.join("tmp", "rate_sheets", f"{params['id']}_original.csv")
    return path


def delete_original_file_path(params):
    try:
        os.remove(get_file_path(params))
    except FileNotFoundError:
        pass


def download_converted_csv_file(converted_file):
    os.makedirs("tmp/rate_sheets", exist_ok=True)
    file_path = os.path.join(
        "tmp", "rate_sheets", f"{converted_file['id']}_original.csv"
    )
    with open(file_path, "wb") as f:
        response = client.get(converted_file["file_url"])
        f.write(response.content)


def get_file_path(params):
    return os.path.join("tmp", "rate_sheets", f"{params['id']}.csv")


def delete_file_path(params):
    try:
        os.remove(get_file_path(params))
    except FileNotFoundError:
        pass


def total_line_keys(params):
    return f"rate_sheet_converted_file_total_lines_{params['id']}"


def set_total_line(params, total_line):
    if rd:
        rd.hset(total_line_hash, total_line_keys(params), total_line)


def get_total_line(params):
    if rd:
        try:
            cached_response = rd.hget(total_line_hash, total_line_keys(params))
            return int(cached_response)
        except:
            return 0


def delete_total_line(params):
    if rd:
        rd.delete(total_line_hash, total_line_keys(params))


def last_line_key(params):
    return f"rate_sheet_converted_file_last_line_{params['id']}"


def set_current_processing_line(last_line, params):
    if rd:
        rd.hset(current_processing_line, last_line_key(params), last_line)


def get_current_processing_line(params):
    if rd:
        try:
            cached_response = rd.hget(current_processing_line, last_line_key(params))
            return int(cached_response)
        except:
            return 0


def delete_last_line(params):
    if rd:
        rd.delete(current_processing_line, last_line_key(params))


def set_initial_counters(converted_file):
    download_converted_csv_file(converted_file)


def errors_present_key(params):
    return f"rate_sheet_converted_file_errors_present_{params['id']}"


def delete_errors_present(params):
    if rd:
        rd.delete(current_processing_line, errors_present_key(params))


def clean_rate_sheet_data(params):
    delete_original_file_path(params)
    delete_file_path(params)
    delete_errors_present(params)
    delete_last_line(params)
    delete_total_line(params)


def convert_date_format(date):
    if not date:
        return date
    parsed_date = parser.parse(date, dayfirst=True)
    return datetime.strptime(str(parsed_date.date()), "%Y-%m-%d")


def processed_percent_key(params):
    return f"rate_sheet_converted_file_processed_percent_{params['id']}"


def set_processed_percent(processed_percent, params):
    if rd:
        rd.hset(
            processed_percent_hash, processed_percent_key(params), processed_percent
        )


def get_processed_percent(params):
    if rd:
        try:
            cached_response = rd.hget(
                processed_percent_hash, processed_percent_key(params)
            )
            return parse_numeric(cached_response)
        except:
            return 0


def valid_hash(hash, present_fields=None, blank_fields=None):
    if present_fields:
        for field in present_fields:
            if field not in hash:
                return False
            if not hash[field]:
                return False
    if blank_fields:
        all_blank = True
        for field in blank_fields:
            if field in hash and hash[field]:
                all_blank = False
        return all_blank
    return True


def get_port_id(port_code):
    try:
        port_code = port_code.strip()
    except:
        port_code = port_code
    filters = {
        "filters": {"type": "seaport", "port_code": port_code, "status": "active"}
    }
    try:
        port_id = maps.list_locations(filters)["list"][0]["id"]
    except:
        port_id = None
    return port_id


def get_shipping_line_id(shipping_line_name):
    try:
        shipping_line_name = shipping_line_name.strip()
        shipping_line_id = get_operators(short_name=shipping_line_name)[0]["id"]
    except:
        shipping_line_id = None
    return shipping_line_id


def get_location_id(q, country_code=None, service_provider_id=None):
    if not q:
        return None

    # pincode filters
    pincode_filters = {"type": "pincode", "postal_code": q, "status": "active"}
    if country_code is not None:
        pincode_filters["country_code"] = country_code
    locations = maps.list_locations({"filters": pincode_filters})["list"]

    # country code filters
    country_code_filters = {"type": "country", "country_code": q, "status": "active"}
    if not locations:
        locations = maps.list_locations({"filters": country_code_filters})["list"]
    if not locations and country_code is not None:
        country_code_filters["country_code"] = country_code
        locations = maps.list_locations({"filters": country_code_filters})["list"]

    # seaport filter with country code
    seaport_filters = {"type": "seaport", "port_code": q, "status": "active"}
    if country_code is not None:
        seaport_filters["country_code"] = country_code
    if not locations:
        locations = maps.list_locations({"filters": seaport_filters})["list"]

    # airport filter with country code
    airport_filters = {"type": "airport", "port_code": q, "status": "active"}
    if country_code is not None:
        airport_filters["country_code"] = country_code
    if not locations:
        locations = maps.list_locations({"filters": airport_filters})["list"]

    # name filter
    name_filters = {"name": q, "status": "active", "type": VALID_LOCATION_TYPES}
    if country_code is not None:
        name_filters["country_code"] = country_code
    if not locations:
        locations = maps.list_locations({"filters": name_filters})["list"]

    # display name filter
    display_name_filters = {
        "display_name": q,
        "status": "active",
        "type": VALID_LOCATION_TYPES,
    }
    if country_code is not None:
        display_name_filters["country_code"] = country_code
    if not locations:
        locations = maps.list_locations({"filters": display_name_filters})["list"]

    return locations[0]["id"] if locations else None


def get_airport_id(port_code, country_code):
    input = {"filters": {"type": "airport", "port_code": port_code, "status": "active"}}
    try:
        locations_data = maps.list_locations(input)
        airport_ids = locations_data["list"][0]["id"]
    except:
        airport_ids = None
    return airport_ids


def get_airline_id(airline_name):
    try:
        airline_name = airline_name.strip()
        airline_id = get_operators(short_name=airline_name, operator_type = 'airline')[0]['id']
    except:
        airline_id = None
    return airline_id