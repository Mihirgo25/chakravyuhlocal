from pydantic import BaseModel
from peewee import *

class FtlFreightData(BaseModel):
    origin_location_id: str
    destination_location_id: str
    origin_region_id: str
    destination_region_id: str
    truck_type: str
    validity_start: str = None
    validity_end: str = None
    currency: str = "INR"

class FtlFreightRate(BaseModel):
    params: list[FtlFreightData]
