from pydantic import BaseModel as pydantic_base_model
from services.fcl_freight_rate.models.fcl_freight_rate_line_item import lineItem
import datetime

class FclFreightRateValidity(pydantic_base_model):
    validity_start: datetime.date
    validity_end: datetime.date
    remarks: list[str] = []
    line_items: list[lineItem] = []
    price: float
    platform_price: float = None
    currency: str
    schedule_type: str = None
    payment_term: str = None
    id: str
    likes_count: int = None
    dislikes_count: int = None

    class Config:
        orm_mode = True
        exclude = ('validity_start', 'validity_end')