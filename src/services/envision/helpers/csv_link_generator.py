from services.rate_sheet.interactions.upload_file import upload_media_file
import os
import pandas as pd
from datetime import datetime
import uuid

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))

def get_csv_url(service, lists):
    
    csv_file_name = generate_file_name(service)
    csv_file_path = os.path.join(ROOT_DIR,'tmp','coverage_stats')
    os.makedirs(csv_file_path, exist_ok=True)
    df = pd.DataFrame(lists)
    file_path = f"{csv_file_path}/{csv_file_name}"
    df.to_csv(file_path, index=False)
    csv_link = upload_media_file(file_path)
    
    return csv_link



def generate_file_name(prefix="file",file_extension=".csv"):
    unique_id = str(uuid.uuid4())
    unique_file_name = f"{prefix}_{unique_id}{file_extension}"
    return unique_file_name