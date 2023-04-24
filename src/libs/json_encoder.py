from fastapi.encoders import jsonable_encoder
from datetime import datetime

def json_encoder(data):
    return jsonable_encoder(data, custom_encoder={datetime: lambda dt: dt.isoformat()+"Z"})
