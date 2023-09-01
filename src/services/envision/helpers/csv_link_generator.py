from services.rate_sheet.interactions.upload_file import upload_media_file
import os
import pandas as pd
from datetime import datetime
import uuid
import time

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))

def get_csv_url(service, lists):
    
    file_name = generate_file_name(service)
    file_path = os.path.join(ROOT_DIR,'tmp',file_name)
    os.makedirs(file_path, exist_ok=True)
    timestamp = str(datetime.now().strftime('%Y%m%d%H%M%S'))

    csv_file_name = f'{file_name}_{timestamp}.csv'
    csv_file_path = os.path.join(file_path, csv_file_name).replace("\\","/")
    
    df = pd.DataFrame(lists)
    df.to_csv(csv_file_path, index=False)
    csv_link = upload_media_file(csv_file_path)
    
    try:
      if os.path.exists(csv_file_path):
          os.remove(csv_file_path)
    except Exception as e:
        print(f"An error occurred while deleting the file: {e}")

    return csv_link



def generate_file_name(prefix="file",file_extension=".csv"):
    unique_id = str(uuid.uuid4())
    unique_file_name = f"{prefix}_{unique_id}{file_extension}"
    return unique_file_name