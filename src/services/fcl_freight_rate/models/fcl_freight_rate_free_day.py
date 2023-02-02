from pydantic import BaseModel as pydantic_base_model
from services.fcl_freight_rate.models.fcl_freight_rate_slab import slab

class freeDay(pydantic_base_model):
  free_limit: int
  slabs: list[slab] = None
  remarks: list[str] = None