from fastapi.encoders import jsonable_encoder as json_encoder
from datetime import datetime

def jsonable_encoder(data):
    return json_encoder(data, custom_encoder={datetime: lambda dt: dt.isoformat()+"Z"})
