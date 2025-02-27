from pydantic import BaseModel
from peewee import *

class CreateLtlFreightRateJob(BaseModel):
    source: str = None
    source_id: str = None
    shipment_id: str = None
    serial_id: int = None
    service_id: str = None
    performed_by_id: str = None
    performed_by_type: str = None
    origin_location_id: str = None
    destination_location_id: str = None
    service_provider_id: str = None
    commodity: str = None
    trip_type: str = None
    transit_time: str = None
    density_factor: float = None
    is_visible: bool = True
    rate_type: str = None

class DeleteLtlFreightRateJob(BaseModel):
    id: str = None
    closing_remarks: list[str] = None
    data: dict = {}
    source_id: str = None
    service_id: str = None
    shipment_id: str = None
    ltl_freight_rate_feedback_ids: list[str] = None
    ltl_freight_rate_request_ids: list[str] = None
    rate_id: str = None
    performed_by_id: str = None
    performed_by_type: str = None
    
class UpdateLtlFreightRateJob(BaseModel):
    id: str
    user_id: str
    performed_by_id: str = None
    performed_by_type: str = None
    
class UpdateLtlFreightRateJobOnRateAddition(BaseModel):
    performed_by_id: str = None
    origin_location_id: str = None
    destination_location_id: str = None
    commodity: str = None
    transit_time: str = None
    density_factor: str = None
    service_provider_id: str = None
