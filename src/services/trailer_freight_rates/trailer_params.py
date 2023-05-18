from pydantic import BaseModel
from datetime import datetime, timedelta,date
from peewee import *
from typing import List
from dateutil.relativedelta import relativedelta

class TrailerConstants(BaseModel):
    country_code: str
    currency_code: str
    nh_toll: float
    tyre: float
    driver: float
    document: float
    handling: float
    maintanance: float
    misc: float
    status: str='active'

class TrailerRateCalculator(BaseModel):
    origin_location_id: str
    destination_location_id: str
    container_size: str
    container_type: str
    trailer_type: str=None
    commodity: str=None
    containers_count: int
    cargo_weight_per_container: float=None
