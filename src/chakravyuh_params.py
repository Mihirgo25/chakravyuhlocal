from pydantic import BaseModel
from datetime import datetime, timedelta, date
from peewee import *
from typing import List


class Slab(BaseModel):
    lower_limit: float
    upper_limit: float
    price: float
    currency: str


class EstimatedLineItems(BaseModel):
    code: str
    unit: str
    lower_price: float
    upper_price: float
    average: float
    stand_dev: float
    size: int
    currency: str
    remarks: list[str] = []
    slabs: list[Slab] = None

class DemandLineItems(BaseModel):
    code: str
    unit: str
    lower_price: float
    upper_price: float
    delta: float
    currency: str
    remarks: list[str] = []
    slabs: list[Slab] = None


class PostFclEstimatedRate(BaseModel):
    performed_by_id: str = None
    performed_by_type: str = None
    origin_location_id: str
    destination_location_id: str
    origin_location_type: str
    destination_location_type: str
    shipping_line_id: str = None
    container_size: str
    container_type: str
    commodity: str = None
    line_items: List[EstimatedLineItems]
    
class PostDemandTransformation(BaseModel):
    performed_by_id: str = None
    performed_by_type: str = None
    origin_location_id: str
    origin_location_type: str
    destination_location_id: str
    destination_location_type: str
    service_type: str
    customer_id: str = None
    net_profit: float = 0
    realised_volume: int = 0
    realised_revenue: float = 0
    realised_currency: str = 'USD'
    line_items: List[DemandLineItems]
    status: str = 'active'
    
class PostRevenueTarget(BaseModel):
    performed_by_id: str = None
    performed_by_type: str = None
    origin_location_id: str
    origin_location_type: str
    destination_location_id: str
    destination_location_type: str
    service_type: str
    customer_id: str = None
    total_loss: float = 0
    total_volume: int = 0
    total_revenue: float = 0
    total_currency: str = 'USD'
    status: str = 'active'
    
