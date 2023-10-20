from pydantic import BaseModel
from peewee import *

class CreateLclCustomsRateJob(BaseModel):
    source: str = None
    source_id: str = None
    shipment_id: str = None
    shipment_serial_id: int = None
    performed_by_id: str = None
    performed_by_type: str = None
    location_id: str = None
    port_id: str = None
    service_provider_id: str = None
    commodity: str = None
    is_visible: bool = True
    rate_type: str = None
    trade_type: str = None

class DeleteLclCustomsRateJob(BaseModel):
    id: str = None
    closing_remarks: list[str] = None
    data: dict = {}
    source_id: str = None
    shipment_id: str = None
    lcl_customs_rate_feedback_ids: list[str] = None
    lcl_customs_rate_request_ids: list[str] = None
    rate_id: str = None
    performed_by_id: str = None
    performed_by_type: str = None
    
class UpdateLclCustomsRateJob(BaseModel):
    id: str
    user_id: str
    performed_by_id: str = None
    performed_by_type: str = None
    
class UpdateLclCustomsRateJobOnRateAddition(BaseModel):
    performed_by_id: str = None
    location_id: str = None
    commodity: str = None
    trade_type: str = None
    service_provider_id: str