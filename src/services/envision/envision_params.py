from pydantic import BaseModel
from peewee import *

class FtlFreightData(BaseModel):
    origin_location_id: str
    destination_location_id: str
    origin_region_id: str = None
    destination_region_id: str = None
    truck_type: str
    validity_start: str = None
    validity_end: str = None
    currency: str = "INR"

class FtlFreightRate(BaseModel):
    params: list[FtlFreightData]

class HaulageFreightData(BaseModel):
    origin_location_id: str
    destination_location_id: str
    container_size: str
    upper_limit: float = None
    validity_start: str = None
    validity_end: str = None
    currency: str = "INR"

class HaulageFreightRate(BaseModel):
    params: list[HaulageFreightData]

class AirFreightData(BaseModel):
    origin_airport_id: str
    destination_airport_id: str
    airline_id: str
    packages_count: int = 1
    volume: float = 1
    weight: float
    date: str = None
    currency: str = "USD"


class AirFreightRate(BaseModel):
    params: list[AirFreightData]
