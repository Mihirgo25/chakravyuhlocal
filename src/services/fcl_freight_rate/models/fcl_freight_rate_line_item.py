from pydantic import BaseModel as pydantic_base_model
from services.fcl_freight_rate.models.fcl_freight_rate_slab import slab

class lineItem(pydantic_base_model):
  location_id: str = None
  code: str
  unit: str
  price: float
  currency: str
  remarks: list[str] = []
  slabs: list[slab] = None