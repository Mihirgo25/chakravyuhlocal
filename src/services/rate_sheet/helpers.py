import os
import httpx
from database.db_session import rd

client = httpx.Client()


current_processing_line = "last_line"
total_line_hash = "total_line"
error_present_hash = "error_present"
processed_percent_hash = "process_percent"

def get_original_file_path(params):
    path = os.path.join("tmp", "rate_sheets", f"{params['id']}_original.csv")
    return path


def delete_original_file_path(params):
    try:
        os.remove(get_file_path(params))
    except FileNotFoundError:
        pass


def download_converted_csv_file(converted_file):
    os.makedirs('tmp/rate_sheets', exist_ok=True)
    file_path = os.path.join('tmp', 'rate_sheets', f"{converted_file['id']}_original.csv")
    with open(file_path, 'wb') as f:
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
    return  f"rate_sheet_converted_file_errors_present_{params['id']}"

def delete_errors_present(params):
    if rd:
        rd.delete(current_processing_line, errors_present_key(params))


def clean_rate_sheet_data(params):
    delete_original_file_path(params)
    delete_file_path(params)
    delete_errors_present(params)
    delete_last_line(params)
    delete_total_line(params)
