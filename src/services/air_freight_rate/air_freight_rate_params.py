from datetime import datetime
from pydantic import BaseModel

class CreateDraftAirFreightRateParams(BaseModel):
    source: str
    rate_id: str = None
    source: str
    origin_airport_id: str
    destination_airport_id: str
    weight_slabs: dict
    min_price: float
    meta_data: dict = {}
    commodity: str
    commodity_type: str = None
    operation_type: str
    price_type: str
    rate_type: str = None
    service_provider_id: str
    airline_id: str
    currency: str
    stacking_type: str
    status: str = 'active'
    source: str
    validity_start: datetime
    validity_end: datetime